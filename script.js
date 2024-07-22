document.addEventListener('DOMContentLoaded', function () {
    const LANGUAGES = {
        "auto": "Auto",
        "af": "Afrikaans",
        "sq": "Albanian",
        "am": "Amharic",
        // Add the rest of the language codes here
    };

    const sourceLangSelect = document.getElementById('source_lang');
    const targetLangSelect = document.getElementById('target_lang');

    for (const [code, name] of Object.entries(LANGUAGES)) {
        const option = document.createElement('option');
        option.value = code;
        option.textContent = name;
        sourceLangSelect.appendChild(option);

        if (code !== 'auto') {
            const optionClone = option.cloneNode(true);
            targetLangSelect.appendChild(optionClone);
        }
    }

    document.getElementById('translate_button').addEventListener('click', () => {
        const inputText = document.getElementById('input_text').value;
        const sourceLang = document.getElementById('source_lang').value;
        const targetLang = document.getElementById('target_lang').value;

        fetch('http://localhost:5000/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: inputText, source_lang: sourceLang, target_lang: targetLang }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(`Error: ${data.error}`);
            } else {
                document.getElementById('output_text').value = data.translation;
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    document.getElementById('speak_input').addEventListener('click', () => {
        // Implement speech-to-text functionality
    });

    document.getElementById('speak_output').addEventListener('click', () => {
        const translation = document.getElementById('output_text').value;
        const targetLang = document.getElementById('target_lang').value;

        fetch('http://localhost:5000/text_to_speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ translation, target_lang: targetLang }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(`Error: ${data.error}`);
            } else {
                const audio = new Audio(data.audio_file);
                audio.play();
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
