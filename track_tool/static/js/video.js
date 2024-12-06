const video = document.getElementById('video-player');
const playBtn = document.getElementById('play-btn');
const rewindBtn = document.getElementById('rewind-btn');
const forwardBtn = document.getElementById('forward-btn');
const speedBtn = document.getElementById('speed-btn');
const slider = document.getElementById('video-slider');
const pipBtn = document.getElementById('pip-toggle');
const carousel = document.getElementById('carousel');
const canvas = document.getElementById('canvas');
const ctx_carr = canvas.getContext('2d');
const currentTimeDisplay = document.getElementById('current-time');
const totalTimeDisplay = document.getElementById('total-time');
const loadingMessage = document.getElementById('loading-message');





let captureTimes = [];  // Armazena os tempos das imagens capturadas
// Função para capturar o frame do vídeo no tempo exato
function captureFrame(time) {
return new Promise((resolve, reject) => {
if (isNaN(time) || time < 0 || time > video.duration) {
    reject("Tempo inválido para captura");
    return;
}

// Pausar o vídeo para garantir que o tempo seja exato
video.pause();
video.currentTime = time;  // Ajusta o vídeo para o tempo exato antes de capturar o frame

// Usar o evento 'seeked' para garantir que o vídeo tenha realmente alcançado o tempo desejado
video.addEventListener('seeked', function capture() {
    // Garantir que o evento 'seeked' foi disparado, e então capturar o frame
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx_carr.drawImage(video, 0, 0, canvas.width, canvas.height);
    const img = document.createElement('img');
    img.classList.add('carousel-image');
    img.src = canvas.toDataURL();
    resolve(img);  // Resolve a promise com a imagem gerada

    // Remover o ouvinte de evento após a captura do frame
    video.removeEventListener('seeked', capture);
});
});
}

// Função para garantir que a duração do vídeo esteja disponível
function waitForVideoDuration() {
return new Promise((resolve, reject) => {
const checkDuration = setInterval(() => {
    if (!isNaN(video.duration) && video.duration > 0) {
        clearInterval(checkDuration);  // Duração válida encontrada, interrompe a verificação
        resolve();
    }
}, 100);  // Verificar a cada 100ms
});
}

// Função para gerar as imagens do carrossel
async function updateCarousel() {
// Espera até que a duração do vídeo esteja disponível
await waitForVideoDuration();

const numImages = 10;  // Dividir o vídeo em 20 partes
const interval = video.duration / numImages;  // Dividir a duração total do vídeo

carousel.innerHTML = '';  // Limpar o carrossel antes de adicionar novas imagens
captureTimes = [];  // Limpar os tempos anteriores

let capturedImages = 0;
for (let i = 0; i < numImages; i++) {
const captureTime = interval * i;

// Verifica se o tempo da captura é válido
if (captureTime < 0 || captureTime > video.duration) {
    console.log(`Tempo de captura inválido: ${captureTime}`);
    continue;
}

try {
    const img = await captureFrame(captureTime);
    img.addEventListener('click', () => {
        // Quando a imagem é clicada, reproduz o vídeo a partir do tempo correto
        video.currentTime = captureTime;
        video.play();
    });
    carousel.appendChild(img);
    captureTimes.push(captureTime);
    capturedImages++;

    if (capturedImages === numImages) {
        console.log("Carrossel atualizado com sucesso!");
    }
} catch (error) {
    console.error("Erro ao capturar o frame: ", error);
}
}
}


// Evento de progresso do vídeo
video.addEventListener('progress', () => {
    if (video.buffered.length > 0) {
        const bufferedEnd = video.buffered.end(video.buffered.length - 1);
        const videoDuration = video.duration;
        const percentage = (bufferedEnd / videoDuration) * 100;
        loadingMessage.innerHTML = `Carregando vídeo... ${Math.round(percentage)}%`;
    }
});

video.addEventListener('canplaythrough', () => {
    loadingMessage.style.display = 'none';  // Esconde a mensagem de carregamento quando o vídeo estiver pronto
});

video.addEventListener('play', () => {
    playBtn.innerHTML = '⏸️';
});

video.addEventListener('pause', () => {
    playBtn.innerHTML = '⏯️';
});

playBtn.addEventListener('click', () => {
    if (video.paused) {
        video.play();
    } else {
        video.pause();
    }
});

rewindBtn.addEventListener('click', () => {
    video.currentTime -= 10;
});
document.getElementById("slow-rewind-btn").addEventListener("click", function() {
    // Lógica de rewind lento (passo menor)
    video.currentTime -= 0.5;
});

forwardBtn.addEventListener('click', () => {
    video.currentTime += 10;
});

document.getElementById("slow-forward-btn").addEventListener("click", function() {
    // Lógica de forward lento (passo menor)
    video.currentTime += 0.5;});


speedBtn.addEventListener('click', () => {
// Lista de velocidades
const speeds = [0.5, 1, 1.5, 2]; 
// A próxima velocidade a ser definida
const currentSpeedIndex = speeds.indexOf(video.playbackRate);
const nextSpeedIndex = (currentSpeedIndex + 1) % speeds.length;

// Atualiza a velocidade de reprodução do vídeo
video.playbackRate = speeds[nextSpeedIndex];

// Atualiza o texto do botão com o novo valor de velocidade
speedBtn.innerHTML = `⚡ ${video.playbackRate}x`;
});
slider.addEventListener('input', () => {
    video.currentTime = (slider.value / 100) * video.duration;
});





video.addEventListener('timeupdate', () => {
    const currentTime = video.currentTime;
    const duration = video.duration;

    slider.value = (currentTime / duration) * 100;

    currentTimeDisplay.innerHTML = formatTime(currentTime);
    totalTimeDisplay.innerHTML = formatTime(duration);
});

function formatTime(timeInSeconds) {
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = Math.floor(timeInSeconds % 60);
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

updateCarousel();