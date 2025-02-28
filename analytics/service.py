from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField, Avg
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import stripe
from django.conf import settings
from decimal import Decimal
from sales.models import SalesOrder, SalesOrderItem
from products.models import Product
from users.models import User
import stripe
import logging
import json
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from .models import Payment
from products.models import Product


class AnalyticsService:
    @staticmethod
    def get_date_range(date_from=None, date_to=None):
        """
        Возвращает диапазон дат для аналитики.
        Принимает строки в формате YYYY-MM-DD или объекты datetime.
        Если даты не указаны, возвращает последние 30 дней.
        """
        try:
            # Обработка начальной даты
            if date_from:
                if isinstance(date_from, str):
                    date_from = timezone.datetime.strptime(date_from, '%Y-%m-%d')
                date_from = timezone.make_aware(
                    date_from.replace(hour=0, minute=0, second=0, microsecond=0)
                ) if timezone.is_naive(date_from) else date_from
            else:
                date_from = timezone.now() - timedelta(days=30)

            # Обработка конечной даты
            if date_to:
                if isinstance(date_to, str):
                    date_to = timezone.datetime.strptime(date_to, '%Y-%m-%d')
                date_to = timezone.make_aware(
                    date_to.replace(hour=23, minute=59, second=59, microsecond=999999)
                ) if timezone.is_naive(date_to) else date_to
            else:
                date_to = timezone.now()

            # Убедимся, что date_from меньше date_to
            if date_from > date_to:
                date_from, date_to = date_to, date_from

        except (ValueError, TypeError):
            # В случае ошибки парсинга дат, используем последние 30 дней
            date_to = timezone.now()
            date_from = date_to - timedelta(days=30)

        return date_from, date_to

    @staticmethod
    def get_trading_volume(date_from=None, date_to=None):
        date_from, date_to = AnalyticsService.get_date_range(date_from, date_to)
        
        volume = SalesOrderItem.objects.filter(
            sales_order__created_at__range=(date_from, date_to),  
            sales_order__status='completed'
        ).aggregate(
            total=Sum(F('quantity') * F('unit_price'), output_field=DecimalField())
        )['total'] or Decimal('0')
        
        return volume

    @staticmethod
    def get_sales_performance(date_from=None, date_to=None):
        date_from, date_to = AnalyticsService.get_date_range(date_from, date_to)
        
        return SalesOrder.objects.filter(
            created_at__range=(date_from, date_to)
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            orders_count=Count('id'),
            total_amount=Sum(
                F('items__quantity') * F('items__unit_price'),
                output_field=DecimalField()
            )
        ).order_by('date')

    @staticmethod
    def get_product_performance(date_from=None, date_to=None):
        date_from, date_to = AnalyticsService.get_date_range(date_from, date_to)
        
        return Product.objects.filter(
            salesorderitem__sales_order__created_at__range=(date_from, date_to),  # Изменено
            salesorderitem__sales_order__status='completed'
        ).annotate(
            sales_count=Count('salesorderitem'),  # Изменено
            revenue=Sum(
                F('salesorderitem__quantity') * F('salesorderitem__unit_price'),  # Изменено
                output_field=DecimalField()
            ),
            avg_price=Avg('salesorderitem__unit_price')  # Изменено
        ).order_by('-revenue')[:10]

    @staticmethod
    def get_top_sellers(date_from=None, date_to=None):
        date_from, date_to = AnalyticsService.get_date_range(date_from, date_to)
        
        return User.objects.filter(
            sales_orders__created_at__range=(date_from, date_to),  # Изменено с orders на sales_orders
            sales_orders__status='completed'
        ).annotate(
            total_sales=Sum(
                F('sales_orders__items__quantity') * F('sales_orders__items__unit_price'),  # Изменено
                output_field=DecimalField()
            ),
            orders_count=Count('sales_orders', distinct=True),  # Изменено
            conversion=ExpressionWrapper(
                (Count('sales_orders', filter=F('sales_orders__status')=='completed', distinct=True) * 100.0) /  # Изменено
                Count('sales_orders', distinct=True),
                output_field=DecimalField(max_digits=5, decimal_places=2)
            )
        ).order_by('-total_sales')[:5]

    @staticmethod
    def get_dashboard_data(date_from=None, date_to=None):
        date_from, date_to = AnalyticsService.get_date_range(date_from, date_to)
        
        return {
            'trading_volume': AnalyticsService.get_trading_volume(date_from, date_to),
            'orders_count': SalesOrder.objects.filter(
                created_at__range=(date_from, date_to),
                status='completed'
            ).count(),
            'active_users': User.objects.filter(
                sales_orders__created_at__range=(date_from, date_to)  # Изменено
            ).distinct().count(),
            'conversion_rate': SalesOrder.objects.filter(
                created_at__range=(date_from, date_to)
            ).aggregate(
                conversion=ExpressionWrapper(
                    (Count('id', filter=F('status')=='completed') * 100.0) /
                    Count('id'),
                    output_field=DecimalField(max_digits=5, decimal_places=2)
                )
            )['conversion'] or Decimal('0'),
            'sales_performance': AnalyticsService.get_sales_performance(date_from, date_to),
            'top_products': AnalyticsService.get_product_performance(date_from, date_to),
            'top_sellers': AnalyticsService.get_top_sellers(date_from, date_to)
        }



# Настройка логгера
logger = logging.getLogger(__name__)

# Инициализация Stripe API с использованием ключа из настроек
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:
    """
    Сервисный класс для работы с платежами через Stripe
    """
    
    @staticmethod
    def create_payment_intent(user, product_id):
        """
        Создаёт Payment Intent в Stripe и соответствующую запись Payment в БД
        
        Args:
            user: Объект пользователя
            product_id: ID продукта для покупки
            
        Returns:
            tuple: (payment_object, client_secret)
        """
        try:
            # Получаем продукт
            product = Product.objects.get(id=product_id)
            
            # Проверяем, есть ли товар в наличии
            if product.stock <= 0:
                raise ValueError("Товар отсутствует в наличии")
            
            amount_in_cents = int(product.price * 100)  # Конвертируем в центы для Stripe
            
            # Создаем метаданные для платежа
            metadata = {
                'product_id': product_id,
                'user_id': user.id,
                'user_email': user.email,
                'product_name': product.name
            }
            
            # Создаем Payment Intent в Stripe
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency="usd",  # Валюта должна соответствовать настройкам вашего аккаунта Stripe
                metadata=metadata,
                description=f"Покупка: {product.name}",
                automatic_payment_methods={"enabled": True},
                receipt_email=user.email
            )
            
            # Создаем запись Payment в БД
            with transaction.atomic():
                payment = Payment.objects.create(
                    user=user,
                    product=product,
                    amount=product.price,
                    currency='USD',
                    payment_intent_id=payment_intent.id,
                    status='pending',
                )
            
            return payment, payment_intent.client_secret
            
        except Product.DoesNotExist:
            logger.error(f"Продукт с ID {product_id} не найден")
            raise ValueError(f"Продукт с ID {product_id} не найден")
            
        except stripe.error.StripeError as e:
            logger.error(f"Ошибка Stripe при создании PaymentIntent: {str(e)}")
            raise ValueError(f"Ошибка платежной системы: {str(e)}")
            
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при создании PaymentIntent: {str(e)}")
            raise ValueError("Произошла ошибка при оформлении платежа")

    @staticmethod
    def handle_payment_webhook(payload, sig_header):
        """
        Обрабатывает webhook-события от Stripe
        
        Args:
            payload: Тело запроса webhook
            sig_header: Заголовок подписи для верификации
            
        Returns:
            dict: Результат обработки события
        """
        # Проверяем сигнатуру события от Stripe
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            # Недействительная полезная нагрузка
            logger.error(f"Недействительная полезная нагрузка: {str(e)}")
            return {'status': 'error', 'message': 'Invalid payload'}
        except stripe.error.SignatureVerificationError as e:
            # Недействительная сигнатура
            logger.error(f"Недействительная сигнатура: {str(e)}")
            return {'status': 'error', 'message': 'Invalid signature'}
        
        # Получаем тип события
        event_type = event['type']
        
        # Обрабатываем разные типы событий
        if event_type == 'payment_intent.succeeded':
            return PaymentService._handle_payment_intent_succeeded(event)
            
        elif event_type == 'payment_intent.payment_failed':
            return PaymentService._handle_payment_intent_failed(event)
            
        # Другие типы событий можно обрабатывать аналогично
        
        return {'status': 'success', 'message': f'Unhandled event type: {event_type}'}

    @staticmethod
    def _handle_payment_intent_succeeded(event):
        """
        Обрабатывает событие успешного платежа
        """
        payment_intent = event.data.object
        payment_intent_id = payment_intent.id
        
        try:
            with transaction.atomic():
                payment = Payment.objects.get(payment_intent_id=payment_intent_id)
                
                # Обновляем запись платежа
                payment.status = 'completed'
                payment.completed_at = timezone.now()
                payment.payment_method = payment_intent.get('payment_method_types', ['card'])[0]
                
                # Сохраняем дополнительные данные из Stripe
                try:
                    if hasattr(payment_intent, 'charges') and payment_intent.charges.data:
                        charge = payment_intent.charges.data[0]
                        if hasattr(charge, 'billing_details'):
                            payment.billing_details = json.loads(json.dumps(charge.billing_details))
                except Exception as e:
                    logger.warning(f"Не удалось получить details из платежа: {str(e)}")
                
                payment.save()
                
                # Уменьшаем остаток товара на 1
                product = payment.product
                if product and product.stock > 0:
                    product.stock -= 1
                    product.save()
                
                logger.info(f"Платеж {payment_intent_id} успешно обработан")
                
                return {
                    'status': 'success', 
                    'message': 'Payment processed successfully', 
                    'payment_id': payment.id
                }
                
        except Payment.DoesNotExist:
            logger.error(f"Платеж с ID {payment_intent_id} не найден в базе данных")
            return {'status': 'error', 'message': 'Payment not found in database'}
            
        except Exception as e:
            logger.error(f"Ошибка при обработке успешного платежа: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def _handle_payment_intent_failed(event):
        """
        Обрабатывает событие неуспешного платежа
        """
        payment_intent = event.data.object
        payment_intent_id = payment_intent.id
        
        try:
            payment = Payment.objects.get(payment_intent_id=payment_intent_id)
            
            # Получаем сообщение об ошибке
            last_error = payment_intent.get('last_payment_error', {})
            error_message = last_error.get('message', 'Unknown payment failure reason')
            
            # Обновляем запись платежа
            payment.status = 'failed'
            payment.error_message = error_message
            payment.save()
            
            logger.info(f"Платеж {payment_intent_id} отмечен как неудачный: {error_message}")
            
            return {
                'status': 'success', 
                'message': 'Payment failure recorded', 
                'payment_id': payment.id
            }
            
        except Payment.DoesNotExist:
            logger.error(f"Платеж с ID {payment_intent_id} не найден в базе данных")
            return {'status': 'error', 'message': 'Payment not found in database'}
            
        except Exception as e:
            logger.error(f"Ошибка при обработке неудачного платежа: {str(e)}")
            return {'status': 'error', 'message': str(e)}


