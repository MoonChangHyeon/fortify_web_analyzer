// src/main/resources/static/assets/js/custom/datatable-initializer.js
$(function () {
    $("#rule_search_table").DataTable({
      // 내보내기 버튼들 (CSV, Excel, PDF, Print)
      dom: "Bfrtip",
      buttons: ["copy", "csv", "excel", "pdf", "print"],
      // 기본 정렬: 룰 이름(0번째 열) 기준으로 오름차순
      order: [[0, "asc"]],
      // 한글 메시지 설정
      language: {
        search: "검색:",
        lengthMenu: "_MENU_ 개씩 보기",
        info: "총 _TOTAL_개 중 _START_에서 _END_까지 표시",
        infoEmpty: "표시할 데이터가 없습니다.",
        infoFiltered: "(총 _MAX_개에서 필터링됨)",
        paginate: {
          first: "처음",
          last: "마지막",
          next: "다음",
          previous: "이전",
        },
      },
    });
  });