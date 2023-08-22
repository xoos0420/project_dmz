let dotsCount = 0;
function onTextareaInput() {
    const textarea = document.getElementById('input_sentence');
    const sendButton = document.getElementById('send_btn_img');
    console.log('들어옴');
    // textarea의 입력 내용이 비어있으면 기본 이미지로 변경
    if (textarea.value.trim() === '') {
        sendButton.src = './send.png'; // 기본 이미지 파일명
    } else {
        sendButton.src = './send_on.png'; // 변경된 이미지 파일명
    }
}
function getRandomValue() {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', 'http://127.0.0.1:8000/', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                const result = JSON.parse(xhr.responseText);
                document.getElementById('but1').innerText = result.random1[0];
                document.getElementById('but2').innerText = result.random2[0];
                document.getElementById('but3').innerText = result.random3[0];
            } else {
                console.error('Error:', xhr.status);
                document.getElementById('but1').innerText = 'Error occurred. Please try again.';
            }
        }
    };
    xhr.send();
}
// 스크롤 내리는 함수
function scrollToBottomOfDiv() {
    console.log(document.getElementById('container').scrollHeight);
    window.scrollTo(0, document.getElementById('container').scrollHeight + 1000)
}
// textarea 입력 내용이 변경될 때마다 onTextareaInput 함수 호출
document.getElementById('input_sentence').addEventListener('input', onTextareaInput);
document.getElementById('input_sentence').addEventListener('keydown', function (e) {
    if (e.keyCode === 13) {
        e.preventDefault();
        send_Sinjoword();
        document.getElementById('input_sentence').value = ``;
        onTextareaInput()
    }
});
function ask_func(question) {
    const chatZoneDiv = document.getElementById("chat_zone");
    const askDiv = document.createElement("div");
    askDiv.className = "ask";
    let askParagraph = document.createElement("p");
    askParagraph.textContent = question
    askDiv.appendChild(askParagraph);
    chatZoneDiv.appendChild(askDiv);
}
function found_last_ask_p() {
    const chatZoneElement = document.querySelector('#chat_zone');
    const lc = chatZoneElement.lastChild;
    const lc2 = lc.lastChild;
    const outputDiv = lc2.lastChild;
    return outputDiv
}
function dot_interval() {
    const outputDiv = found_last_ask_p()
    if (dotsCount < 3) {
        outputDiv.innerHTML += ".";
        dotsCount++;
    }
    else {
        // clearInterval(dotsInterval);
        outputDiv.innerHTML = ".";
        dotsCount = 1;
    }
}
function new_chat() {
    const chatZoneDiv = document.getElementById("chat_zone");
    // 두 번째 자식 요소를 생성합니다.
    const answerContainerDiv = document.createElement("div");
    answerContainerDiv.className = "answer_container";
    const dmzIconDiv = document.createElement("div");
    dmzIconDiv.className = "dmz_icon";
    const dmzIconImg = document.createElement("img");
    dmzIconImg.src = "logo_D.png";
    dmzIconImg.alt = "";
    dmzIconDiv.appendChild(dmzIconImg);
    const dmzIconParagraph = document.createElement("p");
    dmzIconParagraph.textContent = "DMZ";
    dmzIconDiv.appendChild(dmzIconParagraph);
    answerContainerDiv.appendChild(dmzIconDiv);
    const answerDiv = document.createElement("div");
    answerDiv.className = "answer";
    const answerParagraph = document.createElement("p");
    // answerParagraph.textContent = answer
    answerDiv.appendChild(answerParagraph);
    answerContainerDiv.appendChild(answerDiv);
    // chat_zone div에 두 번째 자식 요소를 추가합니다.
    chatZoneDiv.appendChild(answerContainerDiv);
    return answerParagraph;
}
function displayNextCharacter(messages, chatBox, messageIndex, charIndex) {
    console.log('chatbox' + chatBox);
    if (messageIndex < messages.length) {
        const message = messages[messageIndex];
        if (charIndex < message.length) {
            const currentCharacter = message[charIndex];
            chatBox.innerHTML += currentCharacter;
            // chatContainer.scrollTop = chatContainer.scrollHeight; // 스크롤을 아래로 내림
            setTimeout(() => {
                displayNextCharacter(messages, chatBox, messageIndex, charIndex + 1);
            }, 25); // 글자가 나타나는 간격 (ms)
        }
        else {
            chatBox.innerHTML += "<br>";
            setTimeout(() => {
                displayNextCharacter(messages, chatBox, messageIndex + 1, 0);
            }, 125); // 다음 메시지가 나타나는 간격 (ms)
            scrollToBottomOfDiv()
        }
    }
}
function send_Sinjoword() {
    const input_sentence = document.getElementById('input_sentence').value;
    if (input_sentence === '') {
        return;
    }
    ask_func(input_sentence);
    const data = { 'input_sentence': input_sentence };
    // 텍스트 초기화
    // AJAX 요청
    new_chat()
    scrollToBottomOfDiv();
    let dotsInterval = setInterval(dot_interval, 500);
    let xhr = new XMLHttpRequest();
    // 요청 보내는부분
    xhr.open('POST', 'http://127.0.0.1:8000/request', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            // 임시로 버튼 1에 테스트해보기
            if (xhr.status === 200) {
                const outputDiv = found_last_ask_p();
                outputDiv.innerHTML = '';
                clearInterval(dotsInterval);
                dotsCount = 0;
                const result = JSON.parse(xhr.responseText);
                // const answer = [`해당 문장에서 신조어는 "${result.word}"  입니다!`,
                //  `해당 신조어의 뜻은 ${result.mean}이며,`,
                //  `다음은 번역 결과입니다. ${result.sentence}`]
                let answer = [];
                if (result.word == null) {
                    answer = ['신조어가 포함된 문장이 없습니다.', '신조어가 포함된 문장을 입력해주세요.']
                }
                else if (result.word.length == 1) {
                    answer = ['신조어 : '+ result.word,
                    '뜻 : '+result.mean,
                    '',
                    '해석 : '+result.sentence];
                }
                else {
                    for (let i = 0; i < result.word.length; i++) {
                        answer.push('신조어 : '+result.word[i]);
                        answer.push('뜻 : '+result.mean[i]);
                        answer.push('')
                    }
                    answer.push('해석 : '+result.sentence)
                }
                console.log("함수실행");
                console.log(answer);
                displayNextCharacter(answer, outputDiv, 0, 0);
                scrollToBottomOfDiv();
                getRandomValue();
            } else {
                console.error('Error:', xhr.status);
                document.getElementById('but1').innerText = 'Error occurred. Please try again.';
            }
        }
    };
    xhr.send(JSON.stringify(data));
}
function random_click(text) {
    let word;
    if (text == '1') {
        word = document.getElementById('but1').textContent
    }
    else if (text == '2') {
        word = document.getElementById('but2').textContent
    }
    else if (text == '3') {
        word = document.getElementById('but3').textContent
    }
    ask_func(word);
    scrollToBottomOfDiv();
    new_chat()
    let xhr = new XMLHttpRequest();
    const data = { 'input_sentence': word };
    // 요청 보내는부분
    xhr.open('POST', 'http://127.0.0.1:8000/request', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            // 임시로 버튼 1에 테스트해보기
            if (xhr.status === 200) {
                const result = JSON.parse(xhr.responseText);
                const answer = [`해당 신조어의 뜻은 "${result.mean}" 입니다.`]
                const outputDiv = found_last_ask_p();
                displayNextCharacter(answer, outputDiv, 0, 0);
                scrollToBottomOfDiv()
                getRandomValue()
            } else {
                console.error('Error:', xhr.status);
                document.getElementById('but1').innerText = 'Error occurred. Please try again.';
            }
        }
    };
    xhr.send(JSON.stringify(data));
}