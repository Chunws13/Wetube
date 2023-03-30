// 웹페이지 로딩 시
$(document).ready(function() {
    listing();
    $('#save_btn').hide();
});

// 로그아웃
function logout() {
    $.removeCookie('token');
    alert('로그아웃 되었습니다.')
    window.location.href = '/'
}

// 글 쓰기
function posting() {
    let url = $("#url").val();
    let comment = $("#comment").val();
    let star = $("#star").val();
    let writer = document.querySelector('#user_id').textContent;

    let formData = new FormData();
    formData.append("url_give", url);
    formData.append("comment_give", comment);
    formData.append("star_give", star);
    formData.append("writer_give", writer);

    fetch("/movie/post", {
            method: "POST",
            body: formData
        })
        .then((res) => res.json())
        .then((data) => {
            alert(data["msg"]);
            window.location.reload();
        });
}

// 수정하기
function update_btn(title, image, comment, star) {
    $("#post-box").show();
    $('#save_btn').show();
    $('#post_btn').hide();

    window.scrollTo(0, 0);

    $("#title").val(title);
    $("#url").val(image);
    $("#comment").val(comment);
    $("#star").val(star);
}

// 수정
function edit(id) {
    let edit_btn = document.querySelector(`#edit_btn_${id}`);
    let comment = document.querySelector(`#mycomment_${id}`);

    if (edit_btn.textContent == "수정") {
        edit_btn.textContent = "저장";
        comment.contentEditable = true;

    } else {
        edit_btn.textContent = "수정";
        comment.contentEditable = false;

        let formData = new FormData();
        formData.append("id_give", id);
        formData.append("comment_give", comment.textContent)
        fetch("/movie/update", {
                method: "PUT",
                body: formData
            })
            .then((res) => res.json())
            .then((data) => {
                alert(data["msg"])
                window.location.reload();
            });
    }
}

// 삭제하기
function delete_btn(id) {
    let formData = new FormData();
    formData.append("id_give", id);

    fetch("/movie/delete", {
            method: "DELETE",
            body: formData
        })
        .then((res) => res.json())
        .then((data) => {
            alert(data["msg"]);
            window.location.reload();
        });
}

// 등록하기 버튼 토글
function open_box() {
    $("#post-box").show();
}

function close_box() {
    $("#post-box").hide();
}

// 내가 저장한 영상 리스트만 가져오기
function listing() {
    let writer = document.querySelector('#user_id').textContent;
    let personal_form = new FormData();

    personal_form.append("writer_give", writer);

    fetch("/movie", { method: "POST", body: personal_form })
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
                                    <img src="${image}"
                                        class="card-img-top">
                                    <div class="card-body">
                                        <h5 class="card-title">${title}</h5>
                                        <p class="card-text">${desc}</p>
                                        <p id='star_count_${content_id}' contentEditable='false'>${star_repeat}</p>
                                        <p id='mycomment_${content_id}' contentEditable='false'>${comment}</p>
                                        <button id="edit_btn_${content_id}"  type="button" class="btn btn-outline-primary" onclick="edit('${content_id}')">수정</button>
                                        <button id="delete_btn"  type="button" class="btn btn-outline-danger" onclick="delete_btn('${content_id}')">삭제</button>                                        
                                    </div>
                                </div>
                            </div>`;

                $("#cards-box").append(temp_html);
            });
        });
}