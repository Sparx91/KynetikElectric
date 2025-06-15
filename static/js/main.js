// Kynetik Electric - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            if (href && href !== '#') {
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Form validation and enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // File upload preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const files = e.target.files;
            const preview = document.getElementById('file-preview');
            
            if (preview && files.length > 0) {
                preview.innerHTML = '';
                for (let i = 0; i < files.length; i++) {
                    const file = files[i];
                    const fileItem = document.createElement('div');
                    fileItem.className = 'file-preview-item';
                    fileItem.innerHTML = `
                        <span class="file-name">${file.name}</span>
                        <span class="file-size">(${formatFileSize(file.size)})</span>
                    `;
                    preview.appendChild(fileItem);
                }
                preview.style.display = 'block';
            }
        });
    });

    // Quick Quote Calculator
    const quoteForm = document.getElementById('quote-form');
    if (quoteForm) {
        const inputs = quoteForm.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('change', calculateQuote);
        });
    }

    // Troubleshooting Wizard
    const troubleshootingForm = document.getElementById('troubleshooting-form');
    if (troubleshootingForm) {
        const symptomCheckboxes = troubleshootingForm.querySelectorAll('input[type="checkbox"]');
        symptomCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateTroubleshootingForm);
        });
    }

    // Animated counters for statistics
    const counters = document.querySelectorAll('.counter');
    if (counters.length > 0) {
        const observerOptions = {
            threshold: 0.5,
            triggerOnce: true
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                }
            });
        }, observerOptions);

        counters.forEach(counter => {
            observer.observe(counter);
        });
    }

    // Auto-hide alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.classList.contains('alert-permanent')) {
            setTimeout(() => {
                alert.style.opacity = '0';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }, 5000);
        }
    });

    // Loading states for buttons
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-loading')) {
            e.target.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            e.target.disabled = true;
        }
    });

    // Initialize navbar active states
    updateActiveNavItem();
});

// Utility Functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function calculateQuote() {
    const form = document.getElementById('quote-form');
    if (!form) return;

    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    // Basic calculation logic
    let basePrice = 0;
    const sqft = parseFloat(data.square_footage) || 0;
    const devices = parseInt(data.device_count) || 0;

    switch (data.job_type) {
        case 'industrial_install':
            basePrice = sqft * 5 + devices * 100;
            break;
        case 'panel_upgrade':
            basePrice = 2000 + devices * 50;
            break;
        case 'troubleshooting':
            basePrice = 150 + (devices * 25);
            break;
        default:
            basePrice = sqft * 3 + devices * 75;
    }

    // Project size multiplier
    switch (data.project_size) {
        case 'small':
            basePrice *= 0.8;
            break;
        case 'medium':
            basePrice *= 1.0;
            break;
        case 'large':
            basePrice *= 1.2;
            break;
        case 'enterprise':
            basePrice *= 1.5;
            break;
    }

    const estimate = Math.round(basePrice);
    const estimateDisplay = document.getElementById('estimate-display');
    
    if (estimateDisplay && estimate > 0) {
        estimateDisplay.innerHTML = `
            <div class="estimate-result fade-in">
                <div class="estimate-total">$${estimate.toLocaleString()}</div>
                <p class="text-center text-muted">Estimated project cost</p>
                <p class="text-center">
                    <small>This is a rough estimate. Request a formal bid for accurate pricing.</small>
                </p>
                <div class="text-center mt-3">
                    <a href="/bid-request" class="btn btn-primary">Request Formal Bid</a>
                </div>
            </div>
        `;
    }
}

function updateTroubleshootingForm() {
    const form = document.getElementById('troubleshooting-form');
    if (!form) return;

    const checkedSymptoms = form.querySelectorAll('input[type="checkbox"]:checked');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (submitBtn) {
        submitBtn.disabled = checkedSymptoms.length === 0;
    }
}

function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-target'));
    const duration = 2000; // 2 seconds
    const step = target / (duration / 16); // 60 FPS
    let current = 0;

    const timer = setInterval(() => {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current).toLocaleString();
    }, 16);
}

function updateActiveNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// Service worker registration for PWA capabilities
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Future PWA implementation
        console.log('Service Worker support detected');
    });
}

// Error handling for failed requests
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // Could send error reports to admin dashboard in the future
});

// Intersection Observer for animations
const observeElements = () => {
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });

    animatedElements.forEach(el => {
        observer.observe(el);
    });
};

// Initialize animations after DOM content is loaded
document.addEventListener('DOMContentLoaded', observeElements);

// Lazy loading for images
document.addEventListener('DOMContentLoaded', function() {
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        lazyImages.forEach(img => {
            imageObserver.observe(img);
        });
    } else {
        // Fallback for browsers without IntersectionObserver
        lazyImages.forEach(img => {
            img.src = img.dataset.src;
        });
    }
});
