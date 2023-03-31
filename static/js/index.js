// 웹페이지 로딩 시
$(document).ready(function() {
    listing();
    $('#save_btn').hide();
});


// 페이지 로딩 후 초기 화면 로딩 - 수정 필요 (버튼 삭제)
function listing() {
    fetch("/movie")
        .then((res) => res.json())
        .then((data) => {
            let rows = JSON.parse(data["result"]);

            $("#cards-box").empty();

            rows.forEach((a) => {
                let comment = a["comment"];
                let title = a["title"];
                let desc = a["desc"];
                let image = a["image"];
                let star = a["star"];
                let content_id = a['_id']['$oid'];

                let star_repeat = "⭐".repeat(star);

                let temp_html = `<div class="col">
                                    <div class="card h-100">
                                        <img src="${image}" class="card-img-top">
                                        <div class="card-body">
                                            <h5 class="card-title">${title}</h5>
                                            <p class="card-text">${desc}</p>
                                        </div>
                                    </div>
                                </div>`;

                $("#cards-box").append(temp_html);
            });
        });
}

// 로그아웃
function logout() {
    $.removeCookie('token');
    alert('로그아웃 되었습니다.')
    window.location.href = '/'
}