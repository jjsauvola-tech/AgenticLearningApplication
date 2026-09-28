'use strict';

function planImport(files, course) {
  const supported = [], skipped = [];
  for (const file of files) {
    const path = file.webkitRelativePath || file.name;
    if (!/\.(docx|pptx|pdf)$/i.test(file.name) || file.name.startsWith('~$')) {
      skipped.push(path);
      continue;
    }
    const folders = file.webkitRelativePath ? path.split('/').slice(1,-1) : [];
    supported.push({file, path, course:[course.trim(), ...folders].filter(Boolean).join(' / ')});
  }
  supported.sort((a,b)=>a.path.localeCompare(b.path,undefined,{numeric:true}));
  return {supported, skipped};
}

function importDialog(initialFiles) {
  let files = initialFiles ? [...initialFiles] : [];
  modal(t('import'), `<p>${t('folderImportIntro')}</p><div class="stack">
    <label>${t('courseName')}<input id="importCourse" value="${h(S.course||t('materials'))}" maxlength="100"></label>
    <label>${t('chooseFiles')}<input id="importFiles" type="file" accept=".docx,.pdf,.pptx" multiple></label>
    <label>${t('chooseFolder')}<input id="importFolder" type="file" webkitdirectory multiple></label>
    </div><p class="footer-note">${t('importLimit')} ${t('folderImportHint')}</p>
    <div id="importSelection" role="status"></div><div id="importResults"></div>
    <p id="importSummary" role="status" aria-live="polite"></p>
    <div class="buttons"><button id="runImport" class="primary">${t('import')}</button></div>`, () => {
      const preview = () => {
        const plan = planImport(files,$('#importCourse').value);
        $('#importSelection').textContent = `${t('selectedFiles')}: ${plan.supported.length} · ${t('skippedFiles')}: ${plan.skipped.length}`;
        $('#runImport').disabled = !plan.supported.length;
      };
      $('#importFiles').onchange = () => {files=[...$('#importFiles').files];$('#importFolder').value='';preview();};
      $('#importFolder').onchange = () => {files=[...$('#importFolder').files];$('#importFiles').value='';preview();};
      $('#runImport').onclick = () => runImport(files);
      preview();
    });
}

async function runImport(files) {
  if (S.busy) return;
  const plan = planImport(files,$('#importCourse').value);
  if (!plan.supported.length) return;
  const vault = S.active;
  const headers = {'X-ALA-Vault':vault};
  const results = $('#importResults');
  const summary = $('#importSummary');
  const controls = ['#runImport','#importFiles','#importFolder','#importCourse'].map($);
  let imported=0, duplicates=0, failed=0, firstId=null;
  const updateSummary = () => {
    summary.textContent = `${imported+duplicates+failed}/${plan.supported.length} · ${t('success')}: ${imported} · ${t('alreadyImported')}: ${duplicates} · ${t('failedFiles')}: ${failed} · ${t('skippedFiles')}: ${plan.skipped.length}`;
  };
  S.busy=true;
  controls.forEach(c=>c.disabled=true);
  results.replaceChildren();
  updateSummary();
  try {
    for (const item of plan.supported) {
      const row = document.createElement('div');
      row.className='import-row'; row.textContent=t('importing')+' · '+item.path;
      results.append(row);
      try {
        if (!item.file.size || item.file.size>100*1024*1024) throw Error('file_size');
        const result = await api('/api/import',await item.file.arrayBuffer(),{raw:true,headers:{...headers,
          'X-Filename':encodeURIComponent(item.file.name),'X-Course':encodeURIComponent(item.course)}});
        if (result.duplicate) duplicates++; else imported++;
        firstId ||= result.id;
        row.textContent='✓ '+item.path+' · '+(result.duplicate?t('duplicate'):t('success'));
      } catch(e) {
        failed++;row.textContent=item.path+' · '+t(e.message);row.classList.add('error');
      }
      updateSummary();
    }
    if (plan.skipped.length) {
      const detail=document.createElement('details');
      const title=document.createElement('summary'); title.textContent=t('skippedFiles')+' ('+plan.skipped.length+')';
      const list=document.createElement('p'); list.textContent=plan.skipped.join('\n');list.style.whiteSpace='pre-wrap';
      detail.append(title,list);results.append(detail);
    }
    S.documents=await api('/api/documents',undefined,{headers});
    if (firstId) { S.doc=await api('/api/document/'+firstId,undefined,{headers}); S.page=1;S.course='';S.practiceDraft=null; }
    S.view='lecture'; render();
  } catch(e) { fail(e); }
  finally {
    S.busy=false;
    // Keep the completed report visible until the user closes it.
    $('#runImport').disabled=false;$('#runImport').textContent=t('importDone');$('#runImport').onclick=closeModal;
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports={planImport};
} else {
  Object.assign(words.fi, {
    chooseFolder:'Valitse kansio (myös alikansiot)',
    folderImportIntro:'Valitse yksittäisiä tiedostoja tai kokonainen kansio. Kansiotuonti käy myös kaikki alikansiot läpi.',
    folderImportHint:'DOCX, PPTX ja PDF tuodaan. ZIP-, JSON- ja muut tiedostot ohitetaan. Alikansiot näkyvät omina kokoelminaan antamasi kurssinimen alla.',
    selectedFiles:'Tuotavia tiedostoja', skippedFiles:'Ohitettuja tiedostoja', alreadyImported:'Jo varastossa', failedFiles:'Epäonnistuneita'
  });
  Object.assign(words.en, {
    chooseFolder:'Choose a folder (including subfolders)',
    folderImportIntro:'Select individual files or an entire folder. Folder import includes all subfolders.',
    folderImportHint:'DOCX, PPTX and PDF are imported. ZIP, JSON and other files are skipped. Subfolders become collections under the course name you enter.',
    selectedFiles:'Files to import', skippedFiles:'Skipped files', alreadyImported:'Already in vault', failedFiles:'Failed files'
  });
}
