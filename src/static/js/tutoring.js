(function () {
    var MONTHS_FULL = ['January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'];
    var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    var DAY_FULL = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

    var now = new Date();
    var calYear = now.getFullYear();
    var calMonth = now.getMonth();
    var allSlots = [];
    var slotsCache = {};

    var calBody = document.getElementById('cal-body');
    var calLabel = document.getElementById('cal-month-label');
    var dayDetail = document.getElementById('day-detail');
    var dayDetailTitle = document.getElementById('day-detail-title');
    var dayDetailSlots = document.getElementById('day-detail-slots');
    var calContainer = document.getElementById('calendar-container');
    var statsBar = document.getElementById('stats-bar');
    var hasCalendar = !!calBody;

    if (!hasCalendar) { bindPackageButtons(); animateSteps(); return; }

    document.getElementById('cal-prev').addEventListener('click', function () {
        calMonth--; if (calMonth < 0) { calMonth = 11; calYear--; } loadMonth();
    });
    document.getElementById('cal-next').addEventListener('click', function () {
        calMonth++; if (calMonth > 11) { calMonth = 0; calYear++; } loadMonth();
    });
    document.getElementById('day-detail-close').addEventListener('click', function () {
        dayDetail.style.display = 'none'; calContainer.style.display = 'block';
    });

    function loadMonth() {
        var key = calYear + '-' + calMonth;
        calLabel.textContent = MONTHS_FULL[calMonth] + ' ' + calYear;
        if (slotsCache[key]) { allSlots = slotsCache[key]; renderCalendar(); updateStats(); return; }
        calBody.innerHTML = '<div class="cal-loading">loading...</div>';
        fetch('/tutoring/api/slots?year=' + calYear + '&month=' + (calMonth + 1))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                allSlots = data.slots || [];
                slotsCache[key] = allSlots;
                renderCalendar(); updateStats();
            })
            .catch(function () { calBody.innerHTML = '<div class="cal-loading">failed to load.</div>'; });
    }

    function renderCalendar() {
        calBody.innerHTML = '';
        var slotsByDate = {};
        allSlots.forEach(function (s) {
            if (!slotsByDate[s.date]) slotsByDate[s.date] = [];
            slotsByDate[s.date].push(s);
        });
        var firstDay = new Date(calYear, calMonth, 1);
        var lastDay = new Date(calYear, calMonth + 1, 0);
        var startDow = (firstDay.getDay() + 6) % 7;
        var today = new Date(); today.setHours(0, 0, 0, 0);

        for (var i = 0; i < startDow; i++) {
            var e = document.createElement('div'); e.className = 'cal-cell cal-empty'; calBody.appendChild(e);
        }
        for (var d = 1; d <= lastDay.getDate(); d++) {
            var cell = document.createElement('div');
            var ds = calYear + '-' + String(calMonth + 1).padStart(2, '0') + '-' + String(d).padStart(2, '0');
            var cd = new Date(calYear, calMonth, d);
            var slots = slotsByDate[ds] || [];
            var isPast = cd < today;
            cell.className = 'cal-cell';
            if (isPast) cell.classList.add('cal-past');
            if (cd.getTime() === today.getTime()) cell.classList.add('cal-today');
            if (slots.length > 0 && !isPast) {
                cell.classList.add('cal-has-slots');
                if (slots.length >= 5) cell.classList.add('cal-heat-high');
                else if (slots.length >= 3) cell.classList.add('cal-heat-med');
                else cell.classList.add('cal-heat-low');
            }
            var dn = document.createElement('span'); dn.className = 'cal-day-num'; dn.textContent = d;
            cell.appendChild(dn);
            if (slots.length > 0 && !isPast) {
                var b = document.createElement('span'); b.className = 'cal-slot-count'; b.textContent = slots.length;
                cell.appendChild(b);
                cell.dataset.date = ds;
                cell.addEventListener('click', openDay);
            }
            calBody.appendChild(cell);
        }
    }

    function updateStats() {
        var t = allSlots.length;
        var days = {}; allSlots.forEach(function (s) { days[s.date] = true; });
        var dc = Object.keys(days).length;
        if (t === 0) statsBar.innerHTML = '<span class="stat">no availability this month</span>';
        else statsBar.innerHTML = '<span class="stat"><strong>' + t + '</strong> slot' + (t > 1 ? 's' : '') + '</span><span class="stat-sep">&middot;</span><span class="stat"><strong>' + dc + '</strong> day' + (dc > 1 ? 's' : '') + '</span>';
    }

    // ── Day detail: show available times ──
    function openDay() {
        var dateStr = this.dataset.date;
        var parts = dateStr.split('-');
        var dateObj = new Date(parts[0], parts[1] - 1, parts[2]);
        dayDetailTitle.textContent = DAY_FULL[dateObj.getDay()] + ', ' + dateObj.getDate() + ' ' + MONTHS_FULL[dateObj.getMonth()];

        var daySlots = allSlots.filter(function (s) { return s.date === dateStr; });
        dayDetailSlots.innerHTML = '';

        daySlots.forEach(function (slot) {
            var block = document.createElement('div');
            block.className = 'slot-block';

            var header = document.createElement('div');
            header.className = 'slot-block-header';
            header.innerHTML =
                '<span class="slot-block-time">' + slot.start_time + ' \u2014 ' + slot.end_time + '</span>' +
                '<span class="slot-block-dur">' + slot.duration_minutes + 'min</span>';
            block.appendChild(header);

            if (window.__LOGGED_IN__ && window.__HAS_CREDITS__) {
                block.appendChild(buildRecurrencePicker(slot, dateStr, dateObj));
            } else if (window.__LOGGED_IN__) {
                var note = document.createElement('p');
                note.className = 'slot-block-note';
                note.textContent = 'buy a package to book sessions';
                block.appendChild(note);
            } else {
                var link = document.createElement('a');
                link.href = '/tutoring/auth';
                link.className = 'btn btn-primary';
                link.textContent = 'login to book';
                block.appendChild(link);
            }

            dayDetailSlots.appendChild(block);
        });

        calContainer.style.display = 'none';
        dayDetail.style.display = 'block';
        if (typeof gsap !== 'undefined') {
            gsap.from('.slot-block', { opacity: 0, y: 10, duration: 0.3, stagger: 0.06, ease: 'power2.out' });
        }
    }

    // ── Recurrence picker ──
    function buildRecurrencePicker(slot, dateStr, dateObj) {
        var picker = document.createElement('div');
        picker.className = 'recurrence-picker';

        // Frequency options
        var freqRow = document.createElement('div');
        freqRow.className = 'freq-row';

        var options = [
            { value: 'once', label: 'Just once' },
            { value: 'weekly', label: 'Every ' + DAY_FULL[dateObj.getDay()] },
            { value: 'daily', label: 'Every day' },
        ];

        var selectedFreq = 'once';
        var countInput;

        options.forEach(function (opt) {
            var btn = document.createElement('button');
            btn.className = 'freq-btn' + (opt.value === 'once' ? ' freq-btn-active' : '');
            btn.textContent = opt.label;
            btn.addEventListener('click', function () {
                selectedFreq = opt.value;
                freqRow.querySelectorAll('.freq-btn').forEach(function (b) { b.classList.remove('freq-btn-active'); });
                btn.classList.add('freq-btn-active');
                updatePreview();
            });
            freqRow.appendChild(btn);
        });
        picker.appendChild(freqRow);

        // Count (for weekly/daily)
        var countRow = document.createElement('div');
        countRow.className = 'count-row';
        countRow.style.display = 'none';

        var countLabel = document.createElement('span');
        countLabel.className = 'count-label';
        countLabel.textContent = 'How many sessions?';
        countRow.appendChild(countLabel);

        countInput = document.createElement('input');
        countInput.type = 'range';
        countInput.min = '1';
        countInput.max = String(window.__CREDITS__ || 10);
        countInput.value = '4';
        countInput.className = 'count-slider';
        countInput.addEventListener('input', updatePreview);
        countRow.appendChild(countInput);

        var countDisplay = document.createElement('span');
        countDisplay.className = 'count-display';
        countDisplay.textContent = '4';
        countRow.appendChild(countDisplay);

        picker.appendChild(countRow);

        // Preview
        var preview = document.createElement('div');
        preview.className = 'booking-preview';
        picker.appendChild(preview);

        // Note field
        var noteGroup = document.createElement('div');
        noteGroup.className = 'note-group';
        var noteInput = document.createElement('textarea');
        noteInput.className = 'note-input';
        noteInput.placeholder = 'anything you\'d like to cover? (optional)';
        noteInput.maxLength = 500;
        noteGroup.appendChild(noteInput);
        picker.appendChild(noteGroup);

        // Book button
        var bookBtn = document.createElement('button');
        bookBtn.className = 'btn btn-primary btn-full';
        bookBtn.textContent = 'book 1 session (1 credit)';
        picker.appendChild(bookBtn);

        function updatePreview() {
            var count = selectedFreq === 'once' ? 1 : parseInt(countInput.value);
            countDisplay.textContent = count;
            countRow.style.display = selectedFreq === 'once' ? 'none' : 'flex';

            var dates = generateDates(dateStr, selectedFreq, count, dateObj.getDay());
            // Show preview chips
            preview.innerHTML = '';
            dates.forEach(function (d) {
                var p = d.split('-');
                var dt = new Date(p[0], p[1] - 1, p[2]);
                var chip = document.createElement('span');
                chip.className = 'preview-chip';
                chip.textContent = DAY_NAMES[dt.getDay()] + ' ' + dt.getDate() + ' ' + MONTHS[dt.getMonth()];
                preview.appendChild(chip);
            });

            bookBtn.textContent = 'book ' + count + ' session' + (count > 1 ? 's' : '') + ' (' + count + ' credit' + (count > 1 ? 's' : '') + ')';
            bookBtn.onclick = function () { submitBooking(slot, dates, bookBtn, noteInput.value); };
        }

        updatePreview();
        return picker;
    }

    function generateDates(startDate, freq, count, dayOfWeek) {
        var dates = [];
        var parts = startDate.split('-');
        var current = new Date(parts[0], parts[1] - 1, parts[2]);

        for (var i = 0; i < count; i++) {
            dates.push(formatDate(current));
            if (freq === 'weekly') current.setDate(current.getDate() + 7);
            else if (freq === 'daily') current.setDate(current.getDate() + 1);
        }
        return dates;
    }

    function formatDate(d) {
        return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
    }

    function submitBooking(slot, dates, btn, note) {
        var n = dates.length;
        btn.disabled = true;
        btn.textContent = 'booking...';

        fetch('/tutoring/api/book', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start_time: slot.start_time,
                end_time: slot.end_time,
                duration_minutes: slot.duration_minutes,
                dates: dates,
                note: note || '',
            }),
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.ok) window.location.href = '/tutoring/account?booked=' + data.count;
            else { alert(data.error); btn.disabled = false; btn.textContent = 'book ' + n + ' session' + (n > 1 ? 's' : ''); }
        })
        .catch(function () { alert('Something went wrong.'); btn.disabled = false; });
    }

    // ── Buy package ──
    bindPackageButtons();
    function bindPackageButtons() {
        document.querySelectorAll('.buy-package-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var pid = this.dataset.packageId;
                btn.disabled = true; var orig = btn.textContent; btn.textContent = 'redirecting...';
                fetch('/tutoring/checkout', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ package_id: pid }),
                })
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    if (data.checkout_url) window.location.href = data.checkout_url;
                    else { alert(data.error); btn.disabled = false; btn.textContent = orig; }
                })
                .catch(function () { btn.disabled = false; btn.textContent = orig; });
            });
        });
    }

    animateSteps();
    function animateSteps() {
        if (typeof gsap === 'undefined') return;
        gsap.timeline({ defaults: { ease: 'power3.out' } })
            .from('.book-header .heading', { opacity: 0, y: 30, duration: 0.8 })
            .from('.book-header .subtitle', { opacity: 0, y: 15, duration: 0.5 }, '-=0.4')
            .from('.flow-step', { opacity: 0, y: 20, duration: 0.5, stagger: 0.12 }, '-=0.3');
    }

    loadMonth();
})();
