(function () {
    function initFirebase() {
        if (typeof firebase === 'undefined') return null;
        var config = window.__FIREBASE_CONFIG__;
        if (config && config.apiKey && !firebase.apps.length) {
            firebase.initializeApp(config);
        }
        return firebase.auth();
    }

    var auth = null;
    var mode = 'login';

    var tabs = document.querySelectorAll('.auth-tab');
    var form = document.getElementById('auth-form');
    var nameGroup = document.getElementById('name-group');
    var submitBtn = document.getElementById('auth-submit');
    var errorEl = document.getElementById('auth-error');
    var subtitle = document.getElementById('auth-subtitle');

    tabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
            mode = this.dataset.mode;
            tabs.forEach(function (t) { t.classList.remove('active'); });
            this.classList.add('active');

            if (mode === 'register') {
                nameGroup.style.display = 'block';
                submitBtn.textContent = 'register';
                subtitle.textContent = 'create an account to get started.';
            } else {
                nameGroup.style.display = 'none';
                submitBtn.textContent = 'login';
                subtitle.textContent = 'sign in to book sessions and manage your account.';
            }
            errorEl.textContent = '';
        });
    });

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        errorEl.textContent = '';

        if (!auth) {
            auth = initFirebase();
        }
        if (!auth) {
            errorEl.textContent = 'Firebase is still loading, please try again.';
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'loading...';

        var email = document.getElementById('auth-email').value;
        var password = document.getElementById('auth-password').value;
        var name = document.getElementById('auth-name').value;

        var promise;
        if (mode === 'register') {
            promise = auth.createUserWithEmailAndPassword(email, password)
                .then(function (cred) {
                    if (name) {
                        return cred.user.updateProfile({ displayName: name }).then(function () { return cred; });
                    }
                    return cred;
                });
        } else {
            promise = auth.signInWithEmailAndPassword(email, password);
        }

        promise
            .then(function (cred) {
                return cred.user.getIdToken();
            })
            .then(function (idToken) {
                return fetch('/tutoring/api/session-verify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id_token: idToken }),
                });
            })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (data.ok) {
                    window.location.href = '/tutoring/book';
                } else {
                    errorEl.textContent = data.error || 'Authentication failed';
                    submitBtn.disabled = false;
                    submitBtn.textContent = mode;
                }
            })
            .catch(function (err) {
                var msg = err.message || 'Something went wrong';
                msg = msg.replace('Firebase: ', '').replace(/\(auth\/.*\)/, '').trim();
                errorEl.textContent = msg;
                submitBtn.disabled = false;
                submitBtn.textContent = mode;
            });
    });

    // Animate in
    if (typeof gsap !== 'undefined') {
        gsap.from('.auth-page .heading', { opacity: 0, y: 30, duration: 0.8, ease: 'power3.out' });
        gsap.from('.auth-form-container', { opacity: 0, y: 20, duration: 0.6, delay: 0.3, ease: 'power3.out' });
    }
})();
