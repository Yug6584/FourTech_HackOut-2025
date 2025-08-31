document.addEventListener('DOMContentLoaded', () => {
    // --- Mobile Menu ---
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    if (mobileMenuButton) {
        mobileMenuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // --- Page Transition ---
    const navLinks = document.querySelectorAll('a:not([target="_blank"])');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && (href.startsWith('/') || href.includes('.html'))) {
                e.preventDefault();
                document.body.classList.add('fade-out');
                setTimeout(() => {
                    window.location.href = href;
                }, 400);
            }
        });
    });
// Modal logic
    const modal = document.getElementById('joinCommunityModal');
    const closeModal = document.getElementById('closeModalBtn');
    const form = document.getElementById('joinForm');
    const successMsg = document.getElementById('joinSuccess');

    // Delegate event for join button (since it may be re-rendered)
    joinSection.addEventListener('click', function (e) {
        if (e.target && e.target.id === 'joinCommunityBtn') {
            e.preventDefault();
            modal.classList.remove('hidden');
        }
    });

    if (closeModal && form && successMsg) {
        closeModal.addEventListener('click', function () {
            modal.classList.add('hidden');
            form.reset();
            successMsg.classList.add('hidden');
        });

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            // Simulate join action
            localStorage.setItem('communityJoined', 'true');
            successMsg.classList.remove('hidden');
            setTimeout(() => {
                modal.classList.add('hidden');
                successMsg.classList.add('hidden');
                communityJoined = true;
                renderJoinSection();
            }, 1200);
        });

        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                modal.classList.add('hidden');
                form.reset();
                successMsg.classList.add('hidden');
            }
        });
    }
});