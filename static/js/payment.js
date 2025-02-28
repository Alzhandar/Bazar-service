(function() {
    'use strict';

    // Проверяем наличие конфигурации
    if (!window.paymentConfig) {
        console.error('Конфигурация платежей не найдена');
        return;
    }

    // Проверяем загрузку зависимостей
    if (typeof Stripe === 'undefined') {
        console.error('Stripe.js не загружен');
        return;
    }

    if (typeof bootstrap === 'undefined') {
        console.error('Bootstrap не загружен');
        return;
    }

    const config = window.paymentConfig;
    const stripe = Stripe(config.stripePublicKey);

    // Состояние платежа
    let state = {
        elements: null,
        paymentElement: null,
        processing: false
    };

    // DOM элементы
    const elements = {
        buyButton: document.getElementById('buyButton'),
        submitButton: document.getElementById('submit-payment'),
        paymentElement: document.getElementById('payment-element'),
        messageElement: document.getElementById('payment-message'),
        modalElement: document.getElementById('paymentModal')
    };

    // Инициализация модального окна
    const modal = new bootstrap.Modal(elements.modalElement);

    // Функции-помощники
    function toggleLoading(element, isLoading) {
        const loader = element.querySelector('.spinner-border');
        const content = element.querySelector('.button-content');
        
        element.disabled = isLoading;
        
        if (isLoading) {
            content.classList.add('d-none');
            loader.classList.remove('d-none');
        } else {
            content.classList.remove('d-none');
            loader.classList.add('d-none');
        }
    }

    function showError(message) {
        elements.messageElement.textContent = message;
        elements.messageElement.classList.remove('d-none');
    }

    function hideError() {
        elements.messageElement.textContent = '';
        elements.messageElement.classList.add('d-none');
    }

    // Обработчик кнопки покупки
    async function handlePurchase(e) {
        e.preventDefault();
        
        if (state.processing) return;
        state.processing = true;
        
        toggleLoading(elements.buyButton, true);
        hideError();
        
        try {
            console.log('Создание платежа для продукта ID:', config.productId);
            const response = await fetch(`/api/products/${config.productId}/purchase/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': config.csrfToken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    product_id: config.productId,
                    quantity: 1
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ошибка: ${response.status}`);
            }

            const data = await response.json();
            
            // Настраиваем Stripe Elements
            state.elements = stripe.elements({
                clientSecret: data.clientSecret,
                appearance: {
                    theme: 'stripe',
                    variables: {
                        colorPrimary: '#0d6efd'
                    }
                }
            });

            // Создаем и монтируем элемент оплаты
            elements.paymentElement.innerHTML = '';
            state.paymentElement = state.elements.create('payment');
            await state.paymentElement.mount('#payment-element');
            
            // Показываем модальное окно
            modal.show();
            
        } catch (error) {
            console.error('Ошибка:', error);
            alert(error.message || 'Произошла ошибка при создании платежа');
        } finally {
            state.processing = false;
            toggleLoading(elements.buyButton, false);
        }
    }

    // Обработчик кнопки оплаты
    async function handlePayment(e) {
        e.preventDefault();
        
        if (state.processing) return;
        state.processing = true;
        
        toggleLoading(elements.submitButton, true);
        hideError();
        
        try {
            const { error } = await stripe.confirmPayment({
                elements: state.elements,
                confirmParams: {
                    return_url: config.returnUrl
                }
            });

            if (error) {
                throw error;
            }
        } catch (error) {
            console.error('Ошибка платежа:', error);
            showError(error.message || 'Ошибка при обработке платежа');
            state.processing = false;
            toggleLoading(elements.submitButton, false);
        }
    }

    // Привязка обработчиков событий
    elements.buyButton.addEventListener('click', handlePurchase);
    elements.submitButton.addEventListener('click', handlePayment);
    
    console.log('Платежный модуль инициализирован');
})();