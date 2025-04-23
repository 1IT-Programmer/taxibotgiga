// Пример JavaScript-кода для минимальных взаимодействий на стороне клиента
document.addEventListener('DOMContentLoaded', function () {
    // Функция обновления заголовка страницы
    const updateTitle = () => {
        document.title = 'Транспортный сервис';
    };

    // Изменение текста приветствия на главной панели
    const greetUser = () => {
        const greetingElement = document.querySelector('.greeting');
        if (greetingElement) {
            greetingElement.textContent = `Привет, ${localStorage.getItem('currentUser')}`;
        }
    };

    // Применение изменений сразу после загрузки страницы
    updateTitle();
    greetUser();
});
