const buttons = document.querySelectorAll('.button-container');
const contents = document.querySelectorAll('.content > div');

contents.forEach(content => {
    content.style.display = 'none';
});
buttons.forEach(button => {
    button.addEventListener('click', () => {
        const buttonText = button.querySelector('.main-text').textContent;
        const targetId = buttonText.toLowerCase().trim().replace(/[^a-z0-9]/g, '');
        const targetContent = document.querySelector(`.${targetId}`);
        
        if (!targetContent) {
            console.error(`Content section .${targetId} not found`);
            return;
        }
        const isCurrentlyVisible = targetContent.style.display === 'block';
        if (isCurrentlyVisible) {
            contents.forEach(content => {
                content.style.display = 'none';
                content.classList.remove('active');
            });
            buttons.forEach(btn => {
                btn.classList.remove('collapsed');
                btn.classList.remove('inactive');
            });

            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        } else {
            contents.forEach(content => {
                if (content === targetContent) {
                    content.style.display = 'block';
                    void content.offsetWidth;
                    content.classList.add('active');
                } else {
                    content.style.display = 'none';
                    content.classList.remove('active');
                }
            });
            
            buttons.forEach(btn => {
                btn.classList.toggle('collapsed', btn === button);
                btn.classList.toggle('inactive', btn !== button);
            });
            setTimeout(() => {
                targetContent.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }, 100);
        }
    });
});