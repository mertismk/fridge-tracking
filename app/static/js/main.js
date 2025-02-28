document.addEventListener('DOMContentLoaded', function() {
    // Включаем все тултипы
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Автозаполнение текущей даты для новых продуктов
    const dateFields = document.querySelectorAll('input[type="date"]');
    dateFields.forEach(field => {
        if (!field.value) {
            const today = new Date();
            const formattedDate = today.toISOString().substr(0, 10);
            field.value = formattedDate;
        }
    });
    
    // Показываем предупреждение при удалении продукта
    const deleteButtons = document.querySelectorAll('.delete-product');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить этот продукт?')) {
                e.preventDefault();
            }
        });
    });
    
    // Анимация для сообщений
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        alert.style.opacity = '0';
        alert.style.transition = 'opacity 0.5s ease';
        
        setTimeout(() => {
            alert.style.opacity = '1';
        }, 100);
        
        // Автоматическое скрытие сообщений через 5 секунд
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });
});