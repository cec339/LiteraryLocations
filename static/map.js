// Immediately hide splash if already shown this session
try {
    if (window.parent.sessionStorage.getItem('litloc_splash_shown')) {
        document.getElementById('splash').style.display = 'none';
    }
} catch(e) {}

var ALL_BOOKS = __BOOKS_JSON__;
var IS_SEARCH_MODE = __IS_SEARCH_MODE__;
var CENTURY_DATA = __CENTURY_DATA__;
var SELECTED_CENTURY = __SELECTED_CENTURY__;
var LABEL_CENTURIES = __LABEL_CENTURIES__;

// Get the REAL visible viewport height (not the iframe's 2000px)
function getVisibleHeight() {
    // Collect all candidate heights
    var candidates = [];
    // 1. visualViewport is the most accurate on mobile
    if (window.visualViewport) candidates.push(window.visualViewport.height);
    // 2. Parent's visualViewport
    try {
        if (window.parent && window.parent !== window && window.parent.visualViewport) {
            candidates.push(window.parent.visualViewport.height);
        }
    } catch(e) {}
    // 3. Parent's innerHeight
    try {
        if (window.parent && window.parent !== window) {
            candidates.push(window.parent.innerHeight);
        }
    } catch(e) {}
    // 4. Parent's documentElement.clientHeight (excludes scrollbar)
    try {
        if (window.parent && window.parent !== window) {
            candidates.push(window.parent.document.documentElement.clientHeight);
        }
    } catch(e) {}
    // 5. Screen as last resort
    candidates.push(screen.availHeight || screen.height);
    // Pick the smallest reasonable value (> 300px) — that's the actual visible area
    var h = window.innerHeight;
    for (var i = 0; i < candidates.length; i++) {
        if (candidates[i] > 300 && candidates[i] < h) {
            h = candidates[i];
        }
    }
    return h;
}

// Set the CSS variable immediately so CSS heights are correct from the start
document.documentElement.style.setProperty('--real-vh', getVisibleHeight() + 'px');

var _leafletMap = null;
var _clusterGroup = null;
var _isFirstLoad = true;

function toggleLegend() {
    document.getElementById('legend').classList.toggle('show');
}

function formatCentury(c) {
    if (c < 0) return Math.abs(c) + ' BC';
    if (c === 1) return '1 AD';
    var s = String(c);
    var last2 = c % 100;
    var last1 = c % 10;
    var suffix = 'th';
    if (last2 >= 11 && last2 <= 13) suffix = 'th';
    else if (last1 === 1) suffix = 'st';
    else if (last1 === 2) suffix = 'nd';
    else if (last1 === 3) suffix = 'rd';
    return s + suffix;
}

function formatCenturyLong(c) {
    if (c < 0) return Math.abs(c) + ' BC';
    if (c === 1) return '1st Century';
    return formatCentury(c) + ' Century';
}

function getLeafletMap() {
    if (_leafletMap) return _leafletMap;
    for (var key in window) {
        try {
            if (window[key] instanceof L.Map) {
                _leafletMap = window[key];
                return _leafletMap;
            }
        } catch(e) {}
    }
    // Fallback: scan leaflet containers
    var containers = document.querySelectorAll('.leaflet-container');
    for (var i = 0; i < containers.length; i++) {
        if (containers[i]._leaflet_map) {
            _leafletMap = containers[i]._leaflet_map;
            return _leafletMap;
        }
    }
    // Folium stores map refs as map_<hash>
    for (var key in window) {
        if (key.indexOf('map_') === 0 && window[key] && typeof window[key].addLayer === 'function') {
            _leafletMap = window[key];
            return _leafletMap;
        }
    }
    return null;
}

var _markerIcon = null;
function getMarkerIcon() {
    if (_markerIcon) return _markerIcon;
    _markerIcon = L.AwesomeMarkers.icon({
        icon: 'book',
        prefix: 'fa',
        markerColor: 'red'
    });
    return _markerIcon;
}

function escapeHtml(s) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(s));
    return div.innerHTML;
}

function createPopupHtml(book) {
    var yearStr = Math.abs(book.year) + (book.year < 0 ? ' BCE' : '');
    var centuryStr = formatCentury(book.century);
    if (book.century < 0) centuryStr += ' Century BCE';
    else centuryStr += ' Century';
    var html = '<div style="width:280px;font-family:Arial,sans-serif;">' +
        '<h4 style="margin-bottom:10px;color:#2E4057;">' + escapeHtml(book.title) + '</h4>' +
        '<p><b>Author:</b> ' + escapeHtml(book.author) + '</p>' +
        '<p><b>Year:</b> ' + yearStr + '</p>' +
        '<p><b>Century:</b> ' + centuryStr + '</p>' +
        '<p><b>Location:</b> ' + escapeHtml(book.setting_name) + '</p>';
    if (book.why_here) {
        html += '<p><b>Why here:</b> ' + escapeHtml(book.why_here) + '</p>';
    }
    html += '<p><b>Summary:</b> ' + escapeHtml(book.summary) + '</p>' +
        '<p><b>Historical Context:</b> ' + escapeHtml(book.hist) + '</p>' +
        '</div>';
    return html;
}

function showCentury(century) {
    var map = getLeafletMap();
    if (!map) return;
    if (_clusterGroup) {
        _clusterGroup.clearLayers();
    } else {
        _clusterGroup = L.markerClusterGroup();
        map.addLayer(_clusterGroup);
    }
    // Remove any existing Folium-added cluster layers
    map.eachLayer(function(layer) {
        if (layer !== _clusterGroup && layer._group && layer.getAllChildMarkers) {
            map.removeLayer(layer);
        }
    });

    var books = IS_SEARCH_MODE ? ALL_BOOKS : ALL_BOOKS.filter(function(b) { return b.century === century; });
    for (var i = 0; i < books.length; i++) {
        var b = books[i];
        var marker = L.marker([b.lat, b.lng], { icon: getMarkerIcon() });
        marker.bindPopup(createPopupHtml(b), { maxWidth: 320 });
        _clusterGroup.addLayer(marker);
    }

    // Smart viewport: reframe only when most markers are off-screen
    if (books.length > 0) {
        var bounds = L.latLngBounds(books.map(function(b) { return [b.lat, b.lng]; }));
        var _mob = window.innerWidth < 768;
        var _pad = _mob ? [10, 10] : [40, 40];
        var _maxZ = _mob ? 10 : 6;
        if (_isFirstLoad) {
            map.fitBounds(bounds, { padding: _pad, maxZoom: _maxZ });
            // On tall mobile screens, fitBounds optimizes for width leaving grey
            // above/below. Zoom in 2 levels so the map fills the vertical space.
            if (_mob) {
                var z = map.getZoom();
                map.setZoom(Math.min(z + 2, _maxZ));
            }
            _isFirstLoad = false;
        } else {
            var viewBounds = map.getBounds();
            var visibleCount = 0;
            for (var j = 0; j < books.length; j++) {
                if (viewBounds.contains(L.latLng(books[j].lat, books[j].lng))) visibleCount++;
            }
            if (visibleCount < books.length * 0.25) {
                map.flyToBounds(bounds, { padding: _pad, maxZoom: _maxZ, duration: 0.8 });
            }
        }
    }

    SELECTED_CENTURY = century;
}

function updateTimelineSelection(c) {
    var track = document.getElementById('timeline-track');
    var items = track.querySelectorAll('[data-century]');
    for (var i = 0; i < items.length; i++) {
        var el = items[i];
        var elC = parseInt(el.getAttribute('data-century'));
        if (elC === c) {
            el.classList.add('selected');
            var lbl = el.querySelector('.tl-pill-label');
            if (lbl) lbl.classList.add('selected');
        } else {
            el.classList.remove('selected');
            var lbl2 = el.querySelector('.tl-pill-label');
            if (lbl2) lbl2.classList.remove('selected');
        }
    }
    // Mobile: scroll selected into view
    if (isMobile()) {
        var sel = track.querySelector('.selected');
        if (sel) sel.scrollIntoView({ inline: 'center', behavior: 'smooth' });
    }
}

function navigateToCentury(c) {
    showCentury(c);
    updateTimelineSelection(c);
    try {
        var url = new URL(window.parent.location.href);
        if (parseInt(url.searchParams.get('century'), 10) === c) return;
        url.searchParams.set('century', c);
        window.parent.history.pushState({ century: c }, '', url.toString());
    } catch(e) {}
}

function getCenturyFromParentUrl() {
    try {
        var url = new URL(window.parent.location.href);
        var rawCentury = url.searchParams.get('century');
        if (rawCentury === null) return null;
        var century = parseInt(rawCentury, 10);
        for (var i = 0; i < CENTURY_DATA.length; i++) {
            if (CENTURY_DATA[i].c === century) return century;
        }
    } catch(e) {}
    return null;
}

function isMobile() {
    return window.innerWidth <= 768;
}

function buildTimeline() {
    var track = document.getElementById('timeline-track');
    track.innerHTML = '';

    var lastWasNeg = false;
    var firstPos = true;
    var infoEl = document.getElementById('timeline-info');

    for (var i = 0; i < CENTURY_DATA.length; i++) {
        var item = CENTURY_DATA[i];
        var c = item.c;
        var n = item.n;

        if (lastWasNeg && c > 0 && firstPos) {
            var divider = document.createElement('div');
            divider.className = 'tl-divider';
            divider.innerHTML = '<div class="tl-divider-line"></div>';
            track.appendChild(divider);
            firstPos = false;
        }
        if (c < 0) lastWasNeg = true;

        var isPill = LABEL_CENTURIES.indexOf(c) !== -1;

        if (isPill) {
            var pill = document.createElement('div');
            pill.className = 'tl-pill' + (c === SELECTED_CENTURY ? ' selected' : '');
            pill.setAttribute('data-century', c);
            pill.setAttribute('data-count', n);

            var lbl = document.createElement('span');
            lbl.className = 'tl-pill-label' + (c === SELECTED_CENTURY ? ' selected' : '');
            lbl.textContent = formatCentury(c);
            pill.appendChild(lbl);

            var badge = document.createElement('span');
            badge.className = 'tl-badge';
            badge.textContent = n;
            pill.appendChild(badge);

            pill.addEventListener('click', (function(century) {
                return function() { navigateToCentury(century); };
            })(c));

            pill.addEventListener('mouseenter', (function(century, count) {
                return function(e) {
                    if (isMobile()) return;
                    var rect = e.currentTarget.getBoundingClientRect();
                    document.getElementById('tl-century').textContent = formatCenturyLong(century);
                    var bw = count === 1 ? 'book' : 'books';
                    document.getElementById('tl-count').textContent = count + ' ' + bw;
                    infoEl.style.top = (rect.top + rect.height / 2 - 16) + 'px';
                    infoEl.style.left = (rect.right + 8) + 'px';
                    infoEl.classList.add('show');
                };
            })(c, n));
            pill.addEventListener('mouseleave', function() {
                infoEl.classList.remove('show');
            });

            track.appendChild(pill);
        } else {
            var wrap = document.createElement('div');
            wrap.className = 'tl-dot-wrap' + (c === SELECTED_CENTURY ? ' selected' : '');
            wrap.setAttribute('data-century', c);
            wrap.setAttribute('data-count', n);

            var dot = document.createElement('div');
            dot.className = 'tl-dot';
            wrap.appendChild(dot);

            wrap.addEventListener('click', (function(century) {
                return function() { navigateToCentury(century); };
            })(c));

            wrap.addEventListener('mouseenter', (function(century, count) {
                return function(e) {
                    if (isMobile()) return;
                    var rect = e.currentTarget.getBoundingClientRect();
                    document.getElementById('tl-century').textContent = formatCenturyLong(century);
                    var bw = count === 1 ? 'book' : 'books';
                    document.getElementById('tl-count').textContent = count + ' ' + bw;
                    infoEl.style.top = (rect.top + rect.height / 2 - 16) + 'px';
                    infoEl.style.left = (rect.right + 8) + 'px';
                    infoEl.classList.add('show');
                };
            })(c, n));
            wrap.addEventListener('mouseleave', function() {
                infoEl.classList.remove('show');
            });

            track.appendChild(wrap);
        }
    }

    if (isMobile()) {
        setTimeout(function() {
            var sel = track.querySelector('.selected');
            if (sel) sel.scrollIntoView({ inline: 'center', behavior: 'auto' });
        }, 50);
    }
}

buildTimeline();

try {
    window.parent.addEventListener('popstate', function() {
        var century = getCenturyFromParentUrl();
        if (century !== null && century !== SELECTED_CENTURY) {
            showCentury(century);
            updateTimelineSelection(century);
        }
    });
} catch(e) {}

var _resizeTimer;
window.addEventListener('resize', function() {
    clearTimeout(_resizeTimer);
    _resizeTimer = setTimeout(function() {
        buildTimeline();
    }, 200);
});

// Coach Tour (once per session via parent sessionStorage)
var CoachTour = (function() {
    var steps = [];
    var currentStep = 0;
    var spotlightEl = null;
    var tooltipEl = null;
    var autoDismissTimer = null;
    var resizeTimer = null;

    function _isMobile() {
        return window.innerWidth <= 768;
    }

    function buildSteps() {
        steps = [
            {
                target: null,
                title: 'Tap a pin to explore a book',
                text: 'Each dot is a great work. Tap to see details.',
                position: 'below'
            },
            {
                target: '#timeline',
                title: 'Travel through 4,000 years',
                text: 'Jump between centuries using the timeline.',
                desktopPos: 'right',
                mobilePos: 'above'
            }
        ];
        if (!_isMobile()) {
            steps.push({
                target: '#legend-btn',
                title: 'What do the colors mean?',
                text: 'Tap info to see the legend.',
                position: 'above-left'
            });
        }
    }

    function createElements() {
        spotlightEl = document.createElement('div');
        spotlightEl.className = 'coach-spotlight';
        document.body.appendChild(spotlightEl);

        tooltipEl = document.createElement('div');
        tooltipEl.className = 'coach-tooltip';
        document.body.appendChild(tooltipEl);

    }

    function showStep(idx) {
        if (idx < 0 || idx >= steps.length) { dismiss(); return; }
        currentStep = idx;
        var step = steps[idx];

        // Determine cutout rect
        var rect;
        if (step.target) {
            var el = document.querySelector(step.target);
            if (el) {
                rect = el.getBoundingClientRect();
                // Add padding around target
                var pad = 8;
                rect = {
                    left: rect.left - pad,
                    top: rect.top - pad,
                    right: rect.right + pad,
                    bottom: rect.bottom + pad,
                    width: rect.width + pad * 2,
                    height: rect.height + pad * 2
                };
            } else {
                rect = _centerRect();
            }
        } else {
            rect = _centerRect();
        }

        // Spotlight with box-shadow cutout
        var rx = Math.min(rect.width, rect.height) > 60 ? 12 : 8;
        var _vh = getVisibleHeight() + 'px';
        spotlightEl.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:' + _vh + ';z-index:19000;pointer-events:none;opacity:0;transition:opacity 0.4s ease;';
        spotlightEl.innerHTML = '<svg style="position:absolute;top:0;left:0;width:100%;height:100%"><defs><mask id="coach-mask"><rect width="100%" height="100%" fill="white"/><rect x="' + rect.left + '" y="' + rect.top + '" width="' + rect.width + '" height="' + rect.height + '" rx="' + rx + '" fill="black"/></mask></defs><rect width="100%" height="100%" fill="rgba(5,5,15,0.75)" mask="url(#coach-mask)"/></svg>';
        spotlightEl.className = 'coach-spotlight';
        void spotlightEl.offsetWidth;
        spotlightEl.classList.add('visible');

        // Tooltip content
        var pos = step.position || (_isMobile() ? step.mobilePos : step.desktopPos) || 'below';
        var isLast = idx === steps.length - 1;
        var arrowClass = _arrowClass(pos);

        tooltipEl.innerHTML =
            '<div class="coach-arrow ' + arrowClass + '"></div>' +
            '<div class="coach-title">' + step.title + '</div>' +
            '<div class="coach-text">' + step.text + '</div>' +
            '<div class="coach-footer">' +
                '<span class="coach-step-indicator">' + (idx + 1) + ' of ' + steps.length + '</span>' +
                '<div class="coach-actions">' +
                    '<button class="coach-skip" id="coach-skip-btn">Skip</button>' +
                    '<button class="coach-btn" id="coach-next-btn">' + (isLast ? 'Got it!' : 'Next') + '</button>' +
                '</div>' +
            '</div>';

        positionTooltip(rect, pos);
        tooltipEl.className = 'coach-tooltip';
        void tooltipEl.offsetWidth;
        tooltipEl.classList.add('visible');

        document.getElementById('coach-next-btn').addEventListener('click', advance);
        document.getElementById('coach-skip-btn').addEventListener('click', dismiss);

        // Auto-dismiss after 15s
        clearTimeout(autoDismissTimer);
        autoDismissTimer = setTimeout(dismiss, 15000);
    }

    function _centerRect() {
        var cw = window.innerWidth;
        var ch = getVisibleHeight();
        var size = Math.min(cw, ch) * 0.25;
        return {
            left: (cw - size) / 2,
            top: (ch - size) / 2,
            width: size,
            height: size,
            right: (cw + size) / 2,
            bottom: (ch + size) / 2
        };
    }

    function _arrowClass(pos) {
        if (pos === 'below') return 'arrow-up';
        if (pos === 'above' || pos === 'above-left') return 'arrow-down';
        if (pos === 'right') return 'arrow-left';
        if (pos === 'left') return 'arrow-right';
        return 'arrow-up';
    }

    function positionTooltip(rect, pos) {
        var gap = 14;
        var tw = 280;
        if (_isMobile()) tw = 240;

        tooltipEl.style.width = tw + 'px';

        // Reset positioning
        tooltipEl.style.top = '';
        tooltipEl.style.bottom = '';
        tooltipEl.style.left = '';
        tooltipEl.style.right = '';

        if (pos === 'below') {
            tooltipEl.style.left = Math.max(8, Math.min(rect.left, window.innerWidth - tw - 8)) + 'px';
            tooltipEl.style.top = (rect.bottom + gap) + 'px';
        } else if (pos === 'above') {
            tooltipEl.style.left = Math.max(8, Math.min(rect.left, window.innerWidth - tw - 8)) + 'px';
            tooltipEl.style.top = Math.max(8, rect.top - gap - 150) + 'px';
        } else if (pos === 'above-left') {
            tooltipEl.style.left = Math.max(8, rect.right - tw) + 'px';
            tooltipEl.style.top = Math.max(8, rect.top - gap - 150) + 'px';
            // Adjust arrow to right side
            var arrow = tooltipEl.querySelector('.coach-arrow');
            if (arrow) { arrow.style.left = 'auto'; arrow.style.right = '24px'; }
        } else if (pos === 'right') {
            tooltipEl.style.left = (rect.right + gap) + 'px';
            tooltipEl.style.top = rect.top + 'px';
        }
    }

    function advance() {
        clearTimeout(autoDismissTimer);
        if (currentStep + 1 >= steps.length) {
            dismiss();
        } else {
            tooltipEl.classList.remove('visible');
            tooltipEl.classList.add('fade-out');
            setTimeout(function() {
                showStep(currentStep + 1);
            }, 300);
        }
    }

    function dismiss() {
        clearTimeout(autoDismissTimer);
        spotlightEl.classList.remove('visible');
        spotlightEl.classList.add('fade-out');
        tooltipEl.classList.remove('visible');
        tooltipEl.classList.add('fade-out');
        setTimeout(function() {
            if (spotlightEl.parentNode) spotlightEl.parentNode.removeChild(spotlightEl);
            if (tooltipEl.parentNode) tooltipEl.parentNode.removeChild(tooltipEl);
        }, 500);
        try {
            window.parent.sessionStorage.setItem('litloc_tour_shown', '1');
        } catch(e) {}
        window.removeEventListener('resize', _onResize);
        var _map = getLeafletMap();
        if (_map) _map.invalidateSize();
    }

    function _onResize() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (spotlightEl && spotlightEl.parentNode) {
                showStep(currentStep);
            }
        }, 200);
    }

    function start() {
        try {
            if (window.parent.sessionStorage.getItem('litloc_tour_shown')) return;
        } catch(e) {}
        buildSteps();
        createElements();
        showStep(0);
        window.addEventListener('resize', _onResize);
    }

    return { start: start };
})();

// Wait for Leaflet map to be ready, then init markers
(function() {
    var attempts = 0;
    var maxAttempts = 50; // 5 seconds at 100ms intervals
    var timer = setInterval(function() {
        attempts++;
        var map = getLeafletMap();
        if (map) {
            clearInterval(timer);
            // Remove the empty MarkerCluster Folium added
            map.eachLayer(function(layer) {
                if (layer._group || (layer.getAllChildMarkers && typeof layer.getAllChildMarkers === 'function')) {
                    map.removeLayer(layer);
                }
            });
            function forceMapSize() {
                var h = getVisibleHeight();
                // Set CSS variable so all elements (map, timeline, spotlight) use real height
                document.documentElement.style.setProperty('--real-vh', h + 'px');
                var mapEl = map.getContainer();
                if (mapEl) {
                    mapEl.style.height = h + 'px';
                    mapEl.style.width = '100%';
                }
                document.body.style.height = h + 'px';
                document.documentElement.style.height = h + 'px';
                map.invalidateSize();
            }
            forceMapSize();
            window.addEventListener('resize', function() {
                forceMapSize();
            });
            showCentury(SELECTED_CENTURY);
            // Second pass: after the browser has laid out the iframe fully,
            // re-force size and re-fit so mobile doesn't show a tiny globe
            setTimeout(function() {
                forceMapSize();
                // Re-fit to current markers
                var books = IS_SEARCH_MODE ? ALL_BOOKS : ALL_BOOKS.filter(function(b) { return b.century === SELECTED_CENTURY; });
                if (books.length > 0) {
                    var bounds = L.latLngBounds(books.map(function(b) { return [b.lat, b.lng]; }));
                    var _mob = window.innerWidth < 768;
                    map.fitBounds(bounds, { padding: _mob ? [10, 10] : [40, 40], maxZoom: _mob ? 10 : 6 });
                    if (_mob) map.setZoom(Math.min(map.getZoom() + 2, 10));
                }
                // Show splash, then launch coach tour after dismiss
                setTimeout(function() {
                    showSplashThenTour();
                }, 300);
            }, 300);
        } else if (attempts >= maxAttempts) {
            clearInterval(timer);
        }
    }, 100);
})();

// Splash overlay — already visible from HTML if not previously shown
function showSplashThenTour() {
    var splash = document.getElementById('splash');
    // If splash is hidden (already shown this session), go straight to tour
    if (!splash || splash.style.display === 'none') {
        CoachTour.start();
        return;
    }
    // Splash is visible — wire up dismiss
    var autoTimer = null;
    var dismissed = false;
    function dismissSplash() {
        if (dismissed) return;
        dismissed = true;
        clearTimeout(autoTimer);
        splash.classList.add('fade-out');
        setTimeout(function() {
            splash.style.display = 'none';
            CoachTour.start();
        }, 850);
        splash.removeEventListener('click', dismissSplash);
    }
    splash.addEventListener('click', dismissSplash);
    autoTimer = setTimeout(dismissSplash, 8000);
    try {
        window.parent.sessionStorage.setItem('litloc_splash_shown', '1');
    } catch(e) {}
}
