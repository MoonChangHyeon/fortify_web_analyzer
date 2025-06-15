/* /fortify_web_analyzer/app/static/js/upload.js */
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('xml_files');
    const fileListUl = document.getElementById('file-list');
    const fileCountDiv = document.getElementById('file-count');

    if (fileInput) {
        fileInput.addEventListener('change', function(event) {
            fileListUl.innerHTML = '';
            
            const files = event.target.files;
            let externalMetadataFilesCount = 0;

            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                if (file.name.endsWith('externalmetadata.xml')) {
                    externalMetadataFilesCount++;
                    const listItem = document.createElement('li');
                    listItem.textContent = file.webkitRelativePath || file.name;
                    fileListUl.appendChild(listItem);
                }
            }

            fileCountDiv.textContent = `선택된 'externalmetadata.xml' 파일 ${externalMetadataFilesCount}개`;

            if (externalMetadataFilesCount === 0) {
                const listItem = document.createElement('li');
                listItem.textContent = '선택한 폴더에 externalmetadata.xml 파일이 없습니다.';
                listItem.style.color = 'red';
                fileListUl.appendChild(listItem);
            }
        });
    }
});