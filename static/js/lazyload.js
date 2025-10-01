// static/js/lazyload.js
(function(){
const imgs = document.querySelectorAll('img[loading="lazy"][data-src]');
const onInt = (entries, obs) => {
entries.forEach(e => {
if(e.isIntersecting){
const img = e.target; img.src = img.dataset.src; img.removeAttribute('data-src');
obs.unobserve(img);
}
});
};
const obs = new IntersectionObserver(onInt, {rootMargin: '200px'});
imgs.forEach(i => obs.observe(i));
})();