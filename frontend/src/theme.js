const STORAGE_KEY = 'rwandaMuseumTheme';

export function initTheme() {
    const saved = localStorage.getItem(STORAGE_KEY);
    const root = document.documentElement;
    if (saved === 'dark') root.classList.add('dark');
    else root.classList.remove('dark');
}

export function toggleTheme() {
    const root = document.documentElement;
    const next = root.classList.toggle('dark');
    localStorage.setItem(STORAGE_KEY, next ? 'dark' : 'light');
    return next;
}

export function isDarkTheme() {
    return document.documentElement.classList.contains('dark');
}
