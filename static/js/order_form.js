class OrderForm {
    constructor() {
        this.form = document.getElementById('orderForm');
        this.itemsContainer = document.getElementById('orderItems');
        this.addButton = document.getElementById('addItemBtn');
        this.template = document.getElementById('orderItemTemplate');
        this.totalAmount = document.getElementById('totalAmount');
        
        this.itemsCount = parseInt(document.querySelector('[name="items-TOTAL_FORMS"]').value);
        this.maxItems = parseInt(document.querySelector('[name="items-MAX_NUM_FORMS"]').value);
        
        this.initialize();
    }

    initialize() {
        if (this.addButton) {
            this.addButton.addEventListener('click', () => this.addItem());
        }
        this.initExistingItems();
        this.calculateTotal();
        
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.validateForm(e));
        }
    }

    initExistingItems() {
        if (this.itemsContainer) {
            this.itemsContainer.querySelectorAll('.order-item').forEach(item => {
                this.initItemHandlers(item);
            });
        }
    }

    addItem() {
        if (this.itemsCount >= this.maxItems) {
            alert('Достигнуто максимальное количество товаров');
            return;
        }

        const clone = this.template.content.cloneNode(true);
        
        clone.querySelectorAll('[name*="__prefix__"]').forEach(element => {
            element.name = element.name.replace('__prefix__', this.itemsCount);
            element.id = element.id.replace('__prefix__', this.itemsCount);
        });
        
        this.itemsContainer.appendChild(clone);
        
        const newItem = this.itemsContainer.lastElementChild;
        this.initItemHandlers(newItem);
        
        this.itemsCount++;
        document.querySelector('[name="items-TOTAL_FORMS"]').value = this.itemsCount;
        
        this.calculateTotal();
    }

    initItemHandlers(item) {
        const productSelect = item.querySelector('.product-select');
        const quantityInput = item.querySelector('.quantity-input');
        const priceInput = item.querySelector('[name$="-unit_price"]');
        const removeButton = item.querySelector('.remove-item-btn');
        
        if (productSelect) {
            productSelect.addEventListener('change', () => {
                const option = productSelect.options[productSelect.selectedIndex];
                if (option && option.dataset.price) {
                    if (priceInput) {
                        priceInput.value = option.dataset.price;
                    }
                    
                    if (quantityInput && option.dataset.stock) {
                        const stock = parseInt(option.dataset.stock);
                        quantityInput.max = stock;
                        quantityInput.title = `Доступно: ${stock} шт.`;
                    }
                }
                this.calculateTotal();
            });
        }
        
        [quantityInput, priceInput].forEach(input => {
            if (input) {
                input.addEventListener('input', () => this.calculateTotal());
            }
        });
        
        if (removeButton) {
            removeButton.addEventListener('click', () => this.removeItem(item));
        }
    }

    removeItem(item) {
        if (this.itemsCount <= 1) {
            alert('Заказ должен содержать хотя бы один товар');
            return;
        }
        
        item.remove();
        this.itemsCount--;
        
        const totalFormsInput = document.querySelector('[name="items-TOTAL_FORMS"]');
        if (totalFormsInput) {
            totalFormsInput.value = this.itemsCount;
        }
        
        this.calculateTotal();
    }

    calculateTotal() {
        let total = 0;
        
        if (this.itemsContainer) {
            this.itemsContainer.querySelectorAll('.order-item').forEach(item => {
                const quantity = parseFloat(item.querySelector('.quantity-input')?.value) || 0;
                const price = parseFloat(item.querySelector('[name$="-unit_price"]')?.value) || 0;
                total += quantity * price;
            });
        }
        
        if (this.totalAmount) {
            const formatter = new Intl.NumberFormat('ru-RU', {
                style: 'currency',
                currency: 'RUB',
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            
            this.totalAmount.textContent = formatter.format(total);
        }
    }

    validateForm(e) {
        let isValid = true;
        const items = this.itemsContainer?.querySelectorAll('.order-item') || [];
        
        items.forEach(item => {
            const product = item.querySelector('.product-select')?.value;
            const quantity = item.querySelector('.quantity-input')?.value;
            const price = item.querySelector('[name$="-unit_price"]')?.value;
            
            if (!product || !quantity || !price) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            alert('Пожалуйста, заполните все обязательные поля для товаров');
        }

        // Проверка на превышение доступного количества
        items.forEach(item => {
            const productSelect = item.querySelector('.product-select');
            const quantityInput = item.querySelector('.quantity-input');
            
            if (productSelect && quantityInput) {
                const option = productSelect.options[productSelect.selectedIndex];
                const stock = parseInt(option?.dataset.stock) || 0;
                const quantity = parseInt(quantityInput.value) || 0;
                
                if (quantity > stock) {
                    e.preventDefault();
                    alert(`Для товара "${option.text}" доступно только ${stock} шт.`);
                    isValid = false;
                }
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new OrderForm();
});