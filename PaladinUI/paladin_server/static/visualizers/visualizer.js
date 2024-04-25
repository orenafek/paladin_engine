export class Visualizer {
    static addStyle(cssStyles) {
        const styleElements = document.head.getElementsByTagName('style');
        if (!Array.from(styleElements).some((styleElement) => styleElement.innerHTML.includes(`.$ {className}`))) {
            const styleTag = document.createElement('style');
            styleTag.textContent = cssStyles;
            document.head.appendChild(styleTag);
        }
    }
}