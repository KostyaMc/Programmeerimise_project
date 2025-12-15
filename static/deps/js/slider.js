const track = document.querySelector(".slider-track");
const cards = document.querySelectorAll(".player-card");
const nextBtn = document.querySelector(".next");
const prevBtn = document.querySelector(".prev");
const sliderWindow = document.querySelector(".slider-window");

let index = 0;
const cardWidth = cards[0].offsetWidth + 16; // 16px is approx margin

function updateSlider() {
    track.style.transform = `translateX(-${index * cardWidth}px)`;
}

nextBtn.addEventListener("click", () => {
    const maxIndex = cards.length - Math.floor(sliderWindow.offsetWidth / cardWidth);
    if (index < maxIndex) {
        index++;
        updateSlider();
    }
});

prevBtn.addEventListener("click", () => {
    if (index > 0) {
        index--;
        updateSlider();
    }
});
