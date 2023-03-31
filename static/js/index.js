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


// 모달 창 팝업기
function movie_detail(id) {
    // 구현 이전
    fetch(`/movie/detail/${id}`).then((res) => res.json()).then((data) => {
        let detail_info = JSON.parse(data['result']);
        let url = detail_info[0]['url'];
        let title = detail_info[0]['title'];
        let desc = detail_info[0]['desc'];

        let window = `
                    <div id="modal_window" class="modal_window">
                        <iframe width="560" height="315" src="${url}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
                    </div>`
        $('#modal_frame').append(window)


        let modal = document.querySelector('#modal_frame')
        modal.style.display = "flex";

        modal.addEventListener("click", e => {
            modal.style.display = 'none';
            $("#modal_frame").empty();
        })
    })
}