/* IJMMHRD — Client-side JavaScript */

document.addEventListener('DOMContentLoaded', function () {

    // ── Mobile Nav Toggle ────────────────────────────────────
    const toggle = document.querySelector('.nav-toggle');
    const menu = document.querySelector('.nav-menu');
    if (toggle && menu) {
        toggle.addEventListener('click', function () {
            menu.classList.toggle('open');
        });
    }

    // ── Flash Message Auto-dismiss ───────────────────────────
    document.querySelectorAll('.alert').forEach(function (el) {
        setTimeout(function () {
            el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            el.style.opacity = '0';
            el.style.transform = 'translateY(-6px)';
            setTimeout(function () { el.remove(); }, 400);
        }, 5500);
    });

    // ── Copy to Clipboard ────────────────────────────────────
    document.querySelectorAll('.copy-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var text = this.getAttribute('data-copy');
            if (!text) return;
            navigator.clipboard.writeText(text).then(function () {
                var original = btn.textContent;
                btn.textContent = 'Copied!';
                btn.classList.add('copied');
                setTimeout(function () {
                    btn.textContent = original;
                    btn.classList.remove('copied');
                }, 2000);
            });
        });
    });

    // ── Co-author Dynamic Fields ─────────────────────────────
    var addCoAuthor = document.getElementById('add-co-author');
    var coAuthorContainer = document.getElementById('co-authors-container');
    if (addCoAuthor && coAuthorContainer) {
        var coAuthorCount = coAuthorContainer.children.length;
        addCoAuthor.addEventListener('click', function () {
            coAuthorCount++;
            var div = document.createElement('div');
            div.className = 'co-author-fields';
            div.innerHTML =
                '<div class="form-row">' +
                '<div class="form-group"><label>Co-Author ' + coAuthorCount + ' Name</label>' +
                '<input type="text" name="co_author_name" class="form-control" placeholder="Full name"></div>' +
                '<div class="form-group"><label>Email</label>' +
                '<input type="email" name="co_author_email" class="form-control" placeholder="Email address"></div>' +
                '<div class="form-group"><label>Affiliation</label>' +
                '<input type="text" name="co_author_affiliation" class="form-control" placeholder="University / Institution"></div>' +
                '</div>' +
                '<button type="button" class="btn btn-sm btn-danger remove-co-author" style="margin-top:0.5rem">Remove Co-Author</button>';
            coAuthorContainer.appendChild(div);
        });

        coAuthorContainer.addEventListener('click', function (e) {
            if (e.target.classList.contains('remove-co-author')) {
                e.target.closest('.co-author-fields').remove();
            }
        });
    }

    // ── Form Validation ──────────────────────────────────────
    document.querySelectorAll('form[data-validate]').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            var valid = true;
            form.querySelectorAll('[required]').forEach(function (input) {
                if (!input.value.trim()) {
                    input.style.borderColor = '#b91c1c';
                    valid = false;
                } else {
                    input.style.borderColor = '';
                }
            });
            if (!valid) {
                e.preventDefault();
                alert('Please complete all required fields.');
            }
        });
    });

    // ── Confirm Actions ──────────────────────────────────────
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            if (!confirm(this.getAttribute('data-confirm'))) {
                e.preventDefault();
            }
        });
    });

    // ── Citation Generator (APA, IEEE, BibTeX) ───────────────
    var bibtexBtn = document.getElementById('generate-bibtex');
    var apaBtn = document.getElementById('generate-apa');
    var ieeeBtn = document.getElementById('generate-ieee');
    var citationOutput = document.getElementById('citation-output');

    if (citationOutput) {
        function getArticleData() {
            var dataAttr = bibtexBtn ? bibtexBtn.getAttribute('data-article') : null;
            return dataAttr ? JSON.parse(dataAttr) : null;
        }

        if (bibtexBtn) {
            bibtexBtn.addEventListener('click', function () {
                var data = getArticleData();
                if (!data) return;
                var key = 'ijmmhrd' + (data.year || '') + (data.id || '');
                var bib = '@article{' + key + ',\n' +
                    '  title   = {' + (data.title || '') + '},\n' +
                    '  author  = {' + (data.authors || '') + '},\n' +
                    '  journal = {International Journal of Multidisciplinary Modern Research and Development (IJMMHRD)},\n' +
                    '  year    = {' + (data.year || '') + '},\n' +
                    '  volume  = {' + (data.volume || '') + '},\n' +
                    '  number  = {' + (data.issue || '') + '},\n' +
                    '  pages   = {' + (data.pages || '') + '},\n' +
                    '  doi     = {' + (data.doi || '') + '}\n' +
                    '}';
                citationOutput.textContent = bib;
                citationOutput.style.display = 'block';
            });
        }

        if (apaBtn) {
            apaBtn.addEventListener('click', function () {
                var data = getArticleData();
                if (!data) return;
                var apa = (data.authors || 'Author') + ' (' + (data.year || '') + '). ' +
                    data.title + '. International Journal of Multidisciplinary Modern Research and Development, ' +
                    (data.volume ? data.volume : '') + (data.issue ? '(' + data.issue + ')' : '') +
                    (data.pages ? ', ' + data.pages : '') + '.' + (data.doi ? ' https://doi.org/' + data.doi : '');
                citationOutput.textContent = apa;
                citationOutput.style.display = 'block';
            });
        }

        if (ieeeBtn) {
            ieeeBtn.addEventListener('click', function () {
                var data = getArticleData();
                if (!data) return;
                var ieee = (data.authors || 'Author') + ', "' + data.title + '," Int. J. Multidisciplinary Mod. Res. Dev., vol. ' +
                    (data.volume || '1') + ', no. ' + (data.issue || '1') + ', pp. ' + (data.pages || '') + ', ' + (data.year || '') + '.';
                citationOutput.textContent = ieee;
                citationOutput.style.display = 'block';
            });
        }
    }

    // ── Automatic Custom File Upload UI Enhancement ─────────────
    function initFileUploadUI() {
        document.querySelectorAll('input[type="file"]').forEach(function (input) {
            if (input.closest('.custom-file-upload-zone') || input.dataset.noEnhance) return;

            input.style.display = 'none';

            var zone = document.createElement('div');
            zone.className = 'custom-file-upload-zone';

            var accept = input.getAttribute('accept') || 'PDF, DOC, DOCX';
            var promptText = 'Click to select file or drag & drop';

            zone.innerHTML =
                '<div class="upload-icon-wrapper">' +
                '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">' +
                '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />' +
                '</svg>' +
                '</div>' +
                '<div class="upload-prompt">' + promptText + '</div>' +
                '<div class="upload-hint">Accepted formats: ' + accept + '</div>' +
                '<div class="btn-select-file">' +
                '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg>' +
                'Choose File' +
                '</div>' +
                '<div class="file-selected-badge">' +
                '<span class="file-badge-icon">📄</span>' +
                '<div class="file-badge-info">' +
                '<div class="file-badge-name"></div>' +
                '<div class="file-badge-size"></div>' +
                '</div>' +
                '<button type="button" class="btn-remove-file" title="Change file">&times;</button>' +
                '</div>';

            input.parentNode.insertBefore(zone, input);
            zone.appendChild(input);

            zone.addEventListener('click', function (e) {
                if (e.target.classList.contains('btn-remove-file')) {
                    e.stopPropagation();
                    input.value = '';
                    zone.classList.remove('has-file');
                    return;
                }
                input.click();
            });

            function updatePreview() {
                if (input.files && input.files.length > 0) {
                    var file = input.files[0];
                    var nameEl = zone.querySelector('.file-badge-name');
                    var sizeEl = zone.querySelector('.file-badge-size');
                    if (nameEl) nameEl.textContent = file.name;
                    if (sizeEl) {
                        var sizeMB = (file.size / (1024 * 1024)).toFixed(2);
                        sizeEl.textContent = sizeMB + ' MB';
                    }
                    var isPdf = file.name.toLowerCase().endsWith('.pdf');
                    var iconEl = zone.querySelector('.file-badge-icon');
                    if (iconEl) iconEl.textContent = isPdf ? '📄' : '📝';

                    zone.classList.add('has-file');
                } else {
                    zone.classList.remove('has-file');
                }
            }

            input.addEventListener('change', updatePreview);

            ['dragenter', 'dragover'].forEach(function (evtName) {
                zone.addEventListener(evtName, function (e) {
                    e.preventDefault();
                    e.stopPropagation();
                    zone.classList.add('dragover');
                }, false);
            });

            ['dragleave', 'drop'].forEach(function (evtName) {
                zone.addEventListener(evtName, function (e) {
                    e.preventDefault();
                    e.stopPropagation();
                    zone.classList.remove('dragover');
                }, false);
            });

            zone.addEventListener('drop', function (e) {
                var dt = e.dataTransfer;
                if (dt && dt.files && dt.files.length > 0) {
                    input.files = dt.files;
                    updatePreview();
                }
            }, false);
        });
    }

    initFileUploadUI();

    // ── IJMMHRD Built-in Word Editor System ──────────────────────
    function initWordEditors() {
        document.querySelectorAll('textarea[name="content"], textarea[data-word-editor]').forEach(function (textarea) {
            if (textarea.dataset.wordEditorInitialized) return;
            textarea.dataset.wordEditorInitialized = 'true';

            textarea.style.display = 'none';

            var container = document.createElement('div');
            container.className = 'word-editor-container';

            // Build Toolbar HTML
            container.innerHTML =
                '<div class="word-editor-toolbar">' +
                '  <div class="word-toolbar-group">' +
                '    <button type="button" class="word-tool-btn" data-cmd="undo" title="Undo (Ctrl+Z)">↩</button>' +
                '    <button type="button" class="word-tool-btn" data-cmd="redo" title="Redo (Ctrl+Y)">↪</button>' +
                '  </div>' +
                '  <div class="word-toolbar-group">' +
                '    <select class="word-tool-select word-format-block" title="Text Style">' +
                '      <option value="p">Paragraph</option>' +
                '      <option value="h1">Heading 1</option>' +
                '      <option value="h2">Heading 2</option>' +
                '      <option value="h3">Heading 3</option>' +
                '      <option value="h4">Heading 4</option>' +
                '      <option value="blockquote">Quote</option>' +
                '    </select>' +
                '  </div>' +
                '  <div class="word-toolbar-group">' +
                '    <button type="button" class="word-tool-btn" data-cmd="bold" title="Bold (Ctrl+B)"><b>B</b></button>' +
                '    <button type="button" class="word-tool-btn" data-cmd="italic" title="Italic (Ctrl+I)"><i>I</i></button>' +
                '    <button type="button" class="word-tool-btn" data-cmd="underline" title="Underline (Ctrl+U)"><u>U</u></button>' +
                '    <button type="button" class="word-tool-btn" data-cmd="strikeThrough" title="Strikethrough"><s>S</s></button>' +
                '  </div>' +
                '  <div class="word-toolbar-group">' +
                '    <span style="font-size:0.75rem;font-weight:700;color:var(--gray-500);">Text:</span>' +
                '    <input type="color" class="word-color-input word-fore-color" value="#0f172a" title="Font Color">' +
                '    <span style="font-size:0.75rem;font-weight:700;color:var(--gray-500);margin-left:0.25rem;">Highlight:</span>' +
                '    <input type="color" class="word-color-input word-bg-color" value="#fef08a" title="Highlight Color">' +
                '  </div>' +
                '  <div class="word-toolbar-group">' +
                '    <button type="button" class="word-tool-btn" data-cmd="justifyLeft" title="Align Left">⯇ Left</button>' +
                '    <button type="button" class="word-tool-btn" data-cmd="justifyCenter" title="Align Center">≡ Center</button>' +
                '    <button type="button" class="word-tool-btn" data-cmd="justifyRight" title="Align Right">⯈ Right</button>' +
                '    <button type="button" class="word-tool-btn" data-cmd="justifyFull" title="Justify Text">≡≡ Justify</button>' +
                '  </div>' +
                '  <div class="word-toolbar-group">' +
                '    <button type="button" class="word-tool-btn" data-cmd="insertUnorderedList" title="Bulleted List">• List</button>' +
                '    <button type="button" class="word-tool-btn" data-cmd="insertOrderedList" title="Numbered List">1. List</button>' +
                '  </div>' +
                '  <div class="word-toolbar-group">' +
                '    <button type="button" class="word-tool-btn word-insert-link" title="Insert Link">🔗 Link</button>' +
                '    <button type="button" class="word-tool-btn word-insert-image" title="Insert Image">🖼️ Image</button>' +
                '    <button type="button" class="word-tool-btn word-insert-table" title="Insert Table">📊 Table</button>' +
                '    <button type="button" class="word-tool-btn word-insert-alert" title="Insert Callout Box">💬 Callout</button>' +
                '    <button type="button" class="word-tool-btn" data-cmd="insertHorizontalRule" title="Insert Divider">―</button>' +
                '  </div>' +
                '  <div class="word-toolbar-group">' +
                '    <select class="word-tool-select word-insert-template" title="Insert Page Template">' +
                '      <option value="">Insert Preset...</option>' +
                '      <option value="about">About Journal Section</option>' +
                '      <option value="guidelines">Author Guidelines Box</option>' +
                '      <option value="highlights">Key Highlights List</option>' +
                '      <option value="contact">Contact Info Box</option>' +
                '    </select>' +
                '  </div>' +
                '  <div class="word-toolbar-group">' +
                '    <button type="button" class="word-tool-btn" data-cmd="removeFormat" title="Clear Formatting">🧹</button>' +
                '    <button type="button" class="word-tool-btn word-toggle-mode" title="Toggle Visual Word / HTML Code Mode">💻 HTML Code</button>' +
                '  </div>' +
                '</div>' +
                '<div class="word-editor-canvas" contenteditable="true"></div>' +
                '<textarea class="word-editor-html-view"></textarea>' +
                '<div class="word-editor-footer">' +
                '  <span class="word-count-info">Words: 0 | Characters: 0</span>' +
                '  <span class="word-sync-status">Mode: Visual Word Editor</span>' +
                '</div>';

            textarea.parentNode.insertBefore(container, textarea);

            var canvas = container.querySelector('.word-editor-canvas');
            var htmlView = container.querySelector('.word-editor-html-view');
            var formatSelect = container.querySelector('.word-format-block');
            var templateSelect = container.querySelector('.word-insert-template');
            var countInfo = container.querySelector('.word-count-info');
            var syncStatus = container.querySelector('.word-sync-status');
            var toggleBtn = container.querySelector('.word-toggle-mode');

            // Initialize content
            canvas.innerHTML = textarea.value || '<p>Start typing your content here...</p>';
            htmlView.value = canvas.innerHTML;

            function syncToTextarea() {
                var content = isHtmlMode ? htmlView.value : canvas.innerHTML;
                textarea.value = content;

                // Update counter
                var text = isHtmlMode ? htmlView.value.replace(/<[^>]*>/g, '') : canvas.textContent;
                var words = text.trim() ? text.trim().split(/\s+/).length : 0;
                var chars = text.length;
                countInfo.textContent = 'Words: ' + words + ' | Characters: ' + chars;
            }

            canvas.addEventListener('input', syncToTextarea);
            htmlView.addEventListener('input', function () {
                canvas.innerHTML = htmlView.value;
                syncToTextarea();
            });

            // Execute formatting commands
            container.querySelectorAll('[data-cmd]').forEach(function (btn) {
                btn.addEventListener('click', function (e) {
                    e.preventDefault();
                    var cmd = this.getAttribute('data-cmd');
                    document.execCommand(cmd, false, null);
                    canvas.focus();
                    syncToTextarea();
                });
            });

            // Format block dropdown
            if (formatSelect) {
                formatSelect.addEventListener('change', function () {
                    var val = this.value;
                    if (val) {
                        document.execCommand('formatBlock', false, '<' + val + '>');
                        canvas.focus();
                        syncToTextarea();
                    }
                });
            }

            // Text colors
            var foreColorInput = container.querySelector('.word-fore-color');
            if (foreColorInput) {
                foreColorInput.addEventListener('change', function () {
                    document.execCommand('foreColor', false, this.value);
                    canvas.focus();
                    syncToTextarea();
                });
            }

            var bgColorInput = container.querySelector('.word-bg-color');
            if (bgColorInput) {
                bgColorInput.addEventListener('change', function () {
                    document.execCommand('hiliteColor', false, this.value);
                    canvas.focus();
                    syncToTextarea();
                });
            }

            // Insert Link
            var linkBtn = container.querySelector('.word-insert-link');
            if (linkBtn) {
                linkBtn.addEventListener('click', function (e) {
                    e.preventDefault();
                    var url = prompt('Enter URL link (e.g. https://example.com):', 'https://');
                    if (url && url !== 'https://') {
                        document.execCommand('createLink', false, url);
                        canvas.focus();
                        syncToTextarea();
                    }
                });
            }

            // Insert Image
            var imgBtn = container.querySelector('.word-insert-image');
            if (imgBtn) {
                imgBtn.addEventListener('click', function (e) {
                    e.preventDefault();
                    var url = prompt('Enter Image URL:', 'https://');
                    if (url && url !== 'https://') {
                        document.execCommand('insertImage', false, url);
                        canvas.focus();
                        syncToTextarea();
                    }
                });
            }

            // Insert Table
            var tableBtn = container.querySelector('.word-insert-table');
            if (tableBtn) {
                tableBtn.addEventListener('click', function (e) {
                    e.preventDefault();
                    var tableHtml =
                        '<table>' +
                        '  <thead>' +
                        '    <tr><th>Header 1</th><th>Header 2</th><th>Header 3</th></tr>' +
                        '  </thead>' +
                        '  <tbody>' +
                        '    <tr><td>Data 1</td><td>Data 2</td><td>Data 3</td></tr>' +
                        '    <tr><td>Data 4</td><td>Data 5</td><td>Data 6</td></tr>' +
                        '  </tbody>' +
                        '</table><p></p>';
                    document.execCommand('insertHTML', false, tableHtml);
                    canvas.focus();
                    syncToTextarea();
                });
            }

            // Insert Alert / Callout
            var alertBtn = container.querySelector('.word-insert-alert');
            if (alertBtn) {
                alertBtn.addEventListener('click', function (e) {
                    e.preventDefault();
                    var alertHtml = '<div class="alert"><strong>Note:</strong> Enter important callout or notice text here.</div><p></p>';
                    document.execCommand('insertHTML', false, alertHtml);
                    canvas.focus();
                    syncToTextarea();
                });
            }

            // Preset Templates
            if (templateSelect) {
                templateSelect.addEventListener('change', function () {
                    var val = this.value;
                    if (!val) return;

                    var html = '';
                    if (val === 'about') {
                        html = '<h2>About IJMMHRD</h2><p>The International Journal of Multidisciplinary Modern Research and Development (IJMMHRD) is a prestigious peer-reviewed, open-access journal dedicated to publishing high-impact research papers across diverse disciplines.</p><div class="alert"><strong>Open Access Policy:</strong> All articles published in IJMMHRD are freely available online immediately upon publication.</div><p></p>';
                    } else if (val === 'guidelines') {
                        html = '<h2>Author Submission Guidelines</h2><p>Please review the following requirements before submitting your manuscript:</p><ul><li>Original research paper formatted according to IJMMHRD template.</li><li>Abstract must not exceed 300 words.</li><li>Provide 4 to 6 relevant keywords.</li></ul><p></p>';
                    } else if (val === 'highlights') {
                        html = '<h3>Key Features & Benefits</h3><ul><li><b>Rapid Peer Review:</b> Turnaround time within 2 to 3 weeks.</li><li><b>DOI Assignment:</b> Registered Crossref DOI for every published paper.</li><li><b>Global Indexing:</b> High visibility and citation reach.</li></ul><p></p>';
                    } else if (val === 'contact') {
                        html = '<div class="alert"><h3>Editorial Contact</h3><p><b>Email:</b> editor@ijmmhrd.org<br><b>Support Hours:</b> Monday - Friday, 9:00 AM - 6:00 PM IST</p></div><p></p>';
                    }

                    if (html) {
                        document.execCommand('insertHTML', false, html);
                        canvas.focus();
                        syncToTextarea();
                    }
                    this.value = '';
                });
            }

            // Toggle Visual vs HTML Mode
            var isHtmlMode = false;
            if (toggleBtn) {
                toggleBtn.addEventListener('click', function (e) {
                    e.preventDefault();
                    isHtmlMode = !isHtmlMode;
                    if (isHtmlMode) {
                        htmlView.value = canvas.innerHTML;
                        canvas.style.display = 'none';
                        htmlView.style.display = 'block';
                        toggleBtn.textContent = '👁️ Visual View';
                        toggleBtn.classList.add('active');
                        syncStatus.textContent = 'Mode: HTML Source Code View';
                    } else {
                        canvas.innerHTML = htmlView.value;
                        htmlView.style.display = 'none';
                        canvas.style.display = 'block';
                        toggleBtn.textContent = '💻 HTML Code';
                        toggleBtn.classList.remove('active');
                        syncStatus.textContent = 'Mode: Visual Word Editor';
                    }
                    syncToTextarea();
                });
            }

            // Initial sync & count
            syncToTextarea();
        });
    }

    initWordEditors();

    // ── Material Design Custom Date Picker System ─────────────────────
    function initMaterialDatePickers() {
        var overlay = document.getElementById('mdDatePickerOverlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'mdDatePickerOverlay';
            overlay.className = 'md-datepicker-overlay';
            overlay.innerHTML =
                '<div class="md-datepicker-modal">' +
                '  <div class="md-datepicker-header">' +
                '    <div class="md-datepicker-header-label">SELECT DATE</div>' +
                '    <div class="md-datepicker-header-date">' +
                '      <span id="mdHeaderDateText">Mon, Nov 17</span>' +
                '      <span class="md-datepicker-header-edit" id="mdHeaderEditBtn" title="Edit Date">✏️</span>' +
                '    </div>' +
                '  </div>' +
                '  <div class="md-datepicker-body">' +
                '    <div class="md-datepicker-nav">' +
                '      <button type="button" class="md-datepicker-month-select" id="mdMonthYearText">November 2026 ▾</button>' +
                '      <div class="md-datepicker-arrows">' +
                '        <button type="button" class="md-datepicker-arrow-btn" id="mdPrevMonthBtn" title="Previous Month">❮</button>' +
                '        <button type="button" class="md-datepicker-arrow-btn" id="mdNextMonthBtn" title="Next Month">❯</button>' +
                '      </div>' +
                '    </div>' +
                '    <div class="md-datepicker-weekdays">' +
                '      <div class="md-datepicker-weekday">S</div>' +
                '      <div class="md-datepicker-weekday">M</div>' +
                '      <div class="md-datepicker-weekday">T</div>' +
                '      <div class="md-datepicker-weekday">W</div>' +
                '      <div class="md-datepicker-weekday">T</div>' +
                '      <div class="md-datepicker-weekday">F</div>' +
                '      <div class="md-datepicker-weekday">S</div>' +
                '    </div>' +
                '    <div class="md-datepicker-days" id="mdDaysGrid"></div>' +
                '  </div>' +
                '  <div class="md-datepicker-footer">' +
                '    <button type="button" class="md-datepicker-btn" id="mdCancelBtn">CANCEL</button>' +
                '    <button type="button" class="md-datepicker-btn" id="mdOkBtn">OK</button>' +
                '  </div>' +
                '</div>';
            document.body.appendChild(overlay);
        }

        var activeInput = null;
        var today = new Date();
        var selectedDate = new Date();
        var viewYear = today.getFullYear();
        var viewMonth = today.getMonth();

        var headerDateText = document.getElementById('mdHeaderDateText');
        var monthYearText = document.getElementById('mdMonthYearText');
        var prevMonthBtn = document.getElementById('mdPrevMonthBtn');
        var nextMonthBtn = document.getElementById('mdNextMonthBtn');
        var daysGrid = document.getElementById('mdDaysGrid');
        var cancelBtn = document.getElementById('mdCancelBtn');
        var okBtn = document.getElementById('mdOkBtn');

        var monthNames = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ];
        var dayNamesShort = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

        function formatHeaderDate(dateObj) {
            var dayName = dayNamesShort[dateObj.getDay()];
            var monthNameShort = monthNames[dateObj.getMonth()].substring(0, 3);
            var dateNum = dateObj.getDate();
            return dayName + ", " + monthNameShort + " " + dateNum;
        }

        function renderCalendar() {
            monthYearText.textContent = monthNames[viewMonth] + " " + viewYear + " ▾";
            headerDateText.textContent = formatHeaderDate(selectedDate);

            daysGrid.innerHTML = '';

            var firstDayIndex = new Date(viewYear, viewMonth, 1).getDay();
            var daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();

            for (var i = 0; i < firstDayIndex; i++) {
                var emptyDiv = document.createElement('div');
                emptyDiv.className = 'md-datepicker-day empty';
                daysGrid.appendChild(emptyDiv);
            }

            for (var d = 1; d <= daysInMonth; d++) {
                var dayDiv = document.createElement('div');
                dayDiv.className = 'md-datepicker-day';
                dayDiv.textContent = d;

                var isToday = (today.getFullYear() === viewYear && today.getMonth() === viewMonth && today.getDate() === d);
                var isSelected = (selectedDate.getFullYear() === viewYear && selectedDate.getMonth() === viewMonth && selectedDate.getDate() === d);

                if (isToday) dayDiv.classList.add('today');
                if (isSelected) dayDiv.classList.add('selected');

                (function (dayNum) {
                    dayDiv.addEventListener('click', function () {
                        selectedDate = new Date(viewYear, viewMonth, dayNum);
                        renderCalendar();
                    });
                })(d);

                daysGrid.appendChild(dayDiv);
            }
        }

        function openDatePicker(input) {
            activeInput = input;

            var val = input.value;
            if (val && /^\d{4}-\d{2}-\d{2}$/.test(val)) {
                var parts = val.split('-');
                selectedDate = new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10));
            } else {
                selectedDate = new Date();
            }

            viewYear = selectedDate.getFullYear();
            viewMonth = selectedDate.getMonth();

            renderCalendar();
            overlay.classList.add('active');
        }

        function closeDatePicker() {
            overlay.classList.remove('active');
        }

        prevMonthBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            viewMonth--;
            if (viewMonth < 0) {
                viewMonth = 11;
                viewYear--;
            }
            renderCalendar();
        });

        nextMonthBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            viewMonth++;
            if (viewMonth > 11) {
                viewMonth = 0;
                viewYear++;
            }
            renderCalendar();
        });

        cancelBtn.addEventListener('click', function () {
            closeDatePicker();
        });

        okBtn.addEventListener('click', function () {
            if (activeInput) {
                var y = selectedDate.getFullYear();
                var m = String(selectedDate.getMonth() + 1).padStart(2, '0');
                var d = String(selectedDate.getDate()).padStart(2, '0');
                var formattedISO = y + '-' + m + '-' + d;

                activeInput.value = formattedISO;
                activeInput.dispatchEvent(new Event('input', { bubbles: true }));
                activeInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
            closeDatePicker();
        });

        overlay.addEventListener('click', function (e) {
            if (e.target === overlay) {
                closeDatePicker();
            }
        });

        document.addEventListener('click', function (e) {
            if (e.target && (e.target.matches('input[type="date"]') || e.target.classList.contains('md-datepicker-trigger'))) {
                e.preventDefault();
                openDatePicker(e.target);
            }
        });

        document.addEventListener('focusin', function (e) {
            if (e.target && e.target.matches('input[type="date"]')) {
                e.target.blur();
                openDatePicker(e.target);
            }
        });
    }

    initMaterialDatePickers();

});

