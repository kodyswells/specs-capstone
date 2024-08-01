document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card');
    const hoveredCardImg = document.getElementById('hovered-card-img');
    const hoverCardContainer = document.querySelector('.hover-card');

    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            const imgSrc = card.getAttribute('data-img');
            hoveredCardImg.src = imgSrc;
            hoverCardContainer.style.display = 'block';
        });

        card.addEventListener('mouseleave', () => {
            hoverCardContainer.style.display = 'none';
        });
    });
});
