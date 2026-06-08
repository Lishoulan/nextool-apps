/**
 * NextTool Performance Optimizer
 * 页面加载性能优化：懒加载、资源预加载、关键CSS内联
 */

(function() {
    'use strict';

    // 1. 图片懒加载
    function initLazyLoad() {
        const images = document.querySelectorAll('img[data-src]');
        if (!images.length) return;

        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        if (img.dataset.srcset) {
                            img.srcset = img.dataset.srcset;
                        }
                        img.removeAttribute('data-src');
                        img.removeAttribute('data-srcset');
                        observer.unobserve(img);
                    }
                });
            }, { rootMargin: '200px' });

            images.forEach(function(img) {
                observer.observe(img);
            });
        } else {
            // Fallback for old browsers
            images.forEach(function(img) {
                img.src = img.dataset.src;
                if (img.dataset.srcset) {
                    img.srcset = img.dataset.srcset;
                }
                img.removeAttribute('data-src');
                img.removeAttribute('data-srcset');
            });
        }
    }

    // 2. 延迟加载非关键脚本
    function deferNonCriticalScripts() {
        const scripts = document.querySelectorAll('script[data-defer]');
        scripts.forEach(function(script) {
            const newScript = document.createElement('script');
            if (script.src) {
                newScript.src = script.src;
            } else {
                newScript.textContent = script.textContent;
            }
            // Copy attributes
            for (let i = 0; i < script.attributes.length; i++) {
                const attr = script.attributes[i];
                if (attr.name !== 'data-defer') {
                    newScript.setAttribute(attr.name, attr.value);
                }
            }
            script.parentNode.replaceChild(newScript, script);
        });
    }

    // 3. 预加载关键资源
    function preloadCriticalResources() {
        // 预加载CSS
        const cssLinks = document.querySelectorAll('link[rel="preload"][as="style"]');
        cssLinks.forEach(function(link) {
            link.rel = 'stylesheet';
        });
    }

    // 4. 延迟加载广告组件
    function deferAds() {
        setTimeout(function() {
            const adSlots = document.querySelectorAll('[data-ad-slot]');
            if (adSlots.length && typeof adsbygoogle !== 'undefined') {
                adSlots.forEach(function() {
                    (adsbygoogle = window.adsbygoogle || []).push({});
                });
            }
        }, 3000);
    }

    // 5. 性能监控
    function trackPerformance() {
        if (typeof gtag !== 'function') return;
        
        window.addEventListener('load', function() {
            setTimeout(function() {
                const perf = performance.getEntriesByType('navigation')[0];
                if (perf) {
                    gtag('event', 'page_performance', {
                        load_time: Math.round(perf.loadEventEnd - perf.startTime),
                        dom_ready: Math.round(perf.domContentLoadedEventEnd - perf.startTime),
                        ttfb: Math.round(perf.responseStart - perf.startTime)
                    });
                }
            }, 1000);
        });
    }

    // 初始化
    document.addEventListener('DOMContentLoaded', function() {
        initLazyLoad();
        preloadCriticalResources();
        deferAds();
        trackPerformance();
    });

    // 延迟脚本在load后执行
    window.addEventListener('load', function() {
        deferNonCriticalScripts();
    });

})();
