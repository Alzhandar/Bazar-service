/**
 * Компонент обработки платежей через Stripe
 * Отвечает за создание платежной сессии и обработку результатов оплаты
 */
document.addEventListener('DOMContentLoaded', function() {
    // Конфигурация платежного компонента
    const config = window.paymentConfig || {};
    
    if (!config.stripePublicKey) {
        console.error('Stripe API key is not defined');
        return;
    }
    
    // Инициализация Stripe.js
    const stripe = Stripe(config.stripePublicKey);
    let elements;
    let paymentElement;
    let paymentIntentId;
    
    // DOM-элементы
    const buyButton = document.getElementById('buyButton');
    const paymentModal = new bootstrap.Modal(document.getElementById('paymentModal'));
    const submitPaymentButton = document.getElementById('submit-payment');
    const paymentMessage = document.getElementById('payment-message');
    
    /**
     * Инициализация покупки товара
     */
    async function initializePurchase() {
        setLoading(buyButton, true);
        
        try {
            // Создаем платежную сессию на сервере
            const response = await fetch(`/analytics/api/products/${config.productId}/purchase/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': config.csrfToken
                },
                body: JSON.stringify({
                    product_id: config.productId
                })
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.message || 'Failed to create payment session');
            }
            
            paymentIntentId = result.payment_intent_id;
            
            // Инициализация элементов Stripe для формы оплаты
            await initializeStripeElements(result.client_secret);
            
            // Открываем модальное окно оплаты
            paymentModal.show();
            
        } catch (error) {
            console.error('Error initializing purchase:', error);
            showMessage('Не удалось создать сессию оплаты. Пожалуйста, попробуйте позже.', 'danger');
        } finally {
            setLoading(buyButton, false);
        }
    }
    
    /**
     * Инициализация элементов Stripe для отображения формы оплаты
     */
    async function initializeStripeElements(clientSecret) {
        elements = stripe.elements({
            clientSecret: clientSecret,
            appearance: {
                theme: 'stripe',
                variables: {
                    colorPrimary: '#0d6efd',
                    colorBackground: '#ffffff',
                    colorText: '#212529',
                    colorDanger: '#dc3545',
                    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                    spacingUnit: '4px',
                    borderRadius: '4px'
                }
            }
        });
        
        // Создание платежного элемента
        paymentElement = elements.create('payment', {
            layout: {
                type: 'tabs',
                defaultCollapsed: false
            }
        });
        
        // Монтирование формы оплаты в DOM
        paymentElement.mount('#payment-element');
    }
    
    /**
     * Обработка отправки формы оплаты
     */
    async function handlePaymentSubmission() {
        setLoading(submitPaymentButton, true);
        hideMessage();
        
        if (!elements) {
            showMessage('Ошибка инициализации формы оплаты', 'danger');
            setLoading(submitPaymentButton, false);
            return;
        }
        
        try {
            // Подтверждение платежа через Stripe
            const { error } = await stripe.confirmPayment({
                elements,
                confirmParams: {
                    return_url: config.returnUrl,
                    payment_method_data: {
                        billing_details: {}
                    },
                },
                redirect: 'if_required'
            });
            
            if (error) {
                if (error.type === 'card_error' || error.type === 'validation_error') {
                    showMessage(error.message, 'danger');
                } else {
                    showMessage('Произошла непредвиденная ошибка при оплате.', 'danger');
                }
            } else {
                // Платеж прошел успешно без редиректа
                window.location.href = config.returnUrl;
            }
        } catch (e) {
            console.error('Error processing payment:', e);
            showMessage('Ошибка обработки платежа. Пожалуйста, попробуйте еще раз.', 'danger');
        } finally {
            setLoading(submitPaymentButton, false);
        }
    }
    
    /**
     * Показать сообщение пользователю
     */
    function showMessage(messageText, type = 'danger') {
        paymentMessage.textContent = messageText;
        paymentMessage.classList.remove('d-none', 'alert-success', 'alert-danger', 'alert-warning');
        paymentMessage.classList.add(`alert-${type}`);
    }
    
    /**
     * Скрыть сообщение пользователю
     */
    function hideMessage() {
        paymentMessage.classList.add('d-none');
    }
    
    /**
     * Переключение состояния загрузки для кнопок
     */
    function setLoading(button, isLoading) {
        const buttonContent = button.querySelector('.button-content');
        const loadingSpinner = button.querySelector('.spinner-border');
        
        if (isLoading) {
            button.disabled = true;
            buttonContent.classList.add('d-none');
            loadingSpinner.classList.remove('d-none');
        } else {
            button.disabled = false;
            buttonContent.classList.remove('d-none');
            loadingSpinner.classList.add('d-none');
        }
    }
    
    // Слушатели событий
    if (buyButton) {
        buyButton.addEventListener('click', initializePurchase);
    }
    
    if (submitPaymentButton) {
        submitPaymentButton.addEventListener('click', handlePaymentSubmission);
    }
    
    // Слушатель закрытия модального окна - сбрасываем состояние платежного элемента
    document.getElementById('paymentModal').addEventListener('hidden.bs.modal', function() {
        if (paymentElement) {
            paymentElement.destroy();
            elements = null;
            paymentElement = null;
        }
        hideMessage();
    });
});