document.addEventListener("DOMContentLoaded", function () {
    const reservationForm = document.getElementById("reservationForm");

    if (reservationForm) {
        reservationForm.onsubmit = function (event) {
            event.preventDefault(); // 기본 폼 제출 방지

            fetch(this.action, {
                method: "POST",
                body: new FormData(this)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message); // ✅ 한글 메시지 정상 출력
                } else {
                    alert(data.message);
                }
            })
            .catch(error => alert("서버 오류 발생: " + error));
        };
    }
});