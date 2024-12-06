
const videoElement = document.getElementById('video-player');        
const cropButton = document.getElementById('crop-button');
const trackButton = document.getElementById('track-button');
const speedButton = document.getElementById('speed-button');
const draggableSquare = document.getElementById('draggable-square');
const resizeHandle = document.querySelector('.resize-handle');
const cropCanvas = document.getElementById('crop-result');
const videoPath = 'objects/template_video.mp4';
const templatePath = 'objects/template.jpg';

let isDragging = false;
let isResizing = false;
let offsetX, offsetY;
let squareWidth = 100, squareHeight = 100;
let playbackSpeed = 1;
let dataObjects = []; // Armazenamento de dados para objetos e imagens

// Movimentação do quadrado
draggableSquare.addEventListener('mousedown', (e) => {
    if (e.target !== resizeHandle) {
        isDragging = true;
        offsetX = e.clientX - draggableSquare.offsetLeft;
        offsetY = e.clientY - draggableSquare.offsetTop;
        draggableSquare.style.cursor = 'grabbing';

        document.addEventListener('mousemove', moveSquare);
        document.addEventListener('mouseup', () => {
            isDragging = false;
            draggableSquare.style.cursor = 'grab';
            document.removeEventListener('mousemove', moveSquare);
        });
    }
});

function moveSquare(e) {
    if (isDragging) {
        const containerRect = videoElement.getBoundingClientRect();
        let newX = e.clientX - offsetX;
        let newY = e.clientY - offsetY;

        newX = Math.max(0, Math.min(newX, containerRect.width - squareWidth));
        newY = Math.max(0, Math.min(newY, containerRect.height - squareHeight));

        draggableSquare.style.left = `${newX}px`;
        draggableSquare.style.top = `${newY}px`;
    }
}

// Redimensionamento do quadrado
resizeHandle.addEventListener('mousedown', (e) => {
    isResizing = true;
    offsetX = e.clientX;
    offsetY = e.clientY;

    document.addEventListener('mousemove', resizeSquare);
    document.addEventListener('mouseup', () => {
        isResizing = false;
        document.removeEventListener('mousemove', resizeSquare);
    });
    e.stopPropagation();
});

function resizeSquare(e) {
    if (isResizing) {
        const dx = e.clientX - offsetX;
        const dy = e.clientY - offsetY;
        squareWidth = Math.max(50, squareWidth + dx);
        squareHeight = Math.max(50, squareHeight + dy);
        draggableSquare.style.width = `${squareWidth}px`;
        draggableSquare.style.height = `${squareHeight}px`;
        offsetX = e.clientX;
        offsetY = e.clientY;
    }
}



