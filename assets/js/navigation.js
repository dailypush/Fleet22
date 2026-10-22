/* Close the mobile navigation after choosing a destination. */
(() => {
    const navigation = document.getElementById('navbarNav');
    if (!navigation) return;
    navigation.addEventListener('click', event => {
        const link = event.target.closest('a[href]');
        if (!link || !navigation.classList.contains('show') || !window.bootstrap?.Collapse) return;
        const destination = new URL(link.href);
        if (destination.origin === location.origin && destination.pathname === location.pathname && destination.hash) {
            const target = document.getElementById(decodeURIComponent(destination.hash.slice(1)));
            navigation.addEventListener('hidden.bs.collapse', () => target?.scrollIntoView({block: 'start'}), {once: true});
        }
        bootstrap.Collapse.getOrCreateInstance(navigation, {toggle: false}).hide();
    });
})();
