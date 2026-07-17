(function () {
    // ── Cancel booking ──
    document.querySelectorAll('.cancel-booking-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var bookingId = this.dataset.bookingId;
            if (!confirm('Cancel this booking? Your session credit will be restored.')) return;

            btn.disabled = true;
            btn.textContent = 'cancelling...';

            fetch('/tutoring/api/cancel-booking', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ booking_id: bookingId }),
            })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (data.ok) {
                    window.location.reload();
                } else {
                    alert(data.error || 'Failed to cancel booking');
                    btn.disabled = false;
                    btn.textContent = 'cancel';
                }
            })
            .catch(function () {
                alert('Something went wrong.');
                btn.disabled = false;
                btn.textContent = 'cancel';
            });
        });
    });

    // ── GSAP entrance animations ──
    if (typeof gsap !== 'undefined') {
        var tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
        tl.from('.account-page .heading', { opacity: 0, y: 30, duration: 0.8 })
          .from('.credits-banner', { opacity: 0, y: 15, duration: 0.5 }, '-=0.4')
          .from('.account-section', { opacity: 0, y: 20, duration: 0.5, stagger: 0.15 }, '-=0.3');
    }
})();
