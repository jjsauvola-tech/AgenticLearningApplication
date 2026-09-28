'use strict';
Object.assign(words.fi, {
  model_empty_response:'Malli ei palauttanut vastausta. Kokeile uudelleen tai valitse toinen paikallinen malli.',
  goals:'Oppimistavoitteet', newGoal:'Uusi tavoite', editGoal:'Muokkaa tavoitetta',
  goalIntro:'Määritä mitä haluat oppia ja valitse tarvittavat esitiedot. Tavoitteet näkyvät esitietojärjestyksessä koko varastosta. Opiskelumerkintä on oma arviosi, ei osaamisen todistus.',
  noGoals:'Ei vielä tavoitteita. Voit aloittaa myös ilman aineistoa.',
  goalDescription:'Mitä haluat osata?', prerequisites:'Esitietotavoitteet',
  noPrerequisites:'Ei esitietotavoitteita', goalReady:'Ei keskeneräisiä esitietoja',
  goalBlocked:'Kertaa ensin', goalStatus:'Oma opiskelutilanne', ongoing:'Työn alla',
  edit:'Muokkaa', deleteGoal:'Poista tavoite', deleteGoalConfirm:'Poistetaanko tavoite ja sen esitietolinkit? Muut tavoitteet ja aineistot säilyvät.',
  goalSource:'Linkki aineistoon', noGoalSource:'Ei aineistolinkkiä', keepGoalSource:'Säilytä nykyinen aineistolinkki',
  useGoalSource:'Linkitä avoinna olevaan aineistokohtaan',
  goal_title_required:'Kirjoita tavoitteelle otsikko (enintään 200 merkkiä).',
  goal_cycle:'Esitietolinkit muodostaisivat kehän. Valitse toiset esitiedot.',
  goal_missing_prerequisite:'Esitietotavoitetta ei löydy tästä varastosta.', invalid_goal:'Tarkista tavoitteen tiedot.'
});
Object.assign(words.en, {
  model_empty_response:'The model returned no answer. Try again or select another local model.',
  goals:'Learning goals', newGoal:'New goal', editGoal:'Edit goal',
  goalIntro:'Define what you want to learn and select its prerequisites. Goals from the whole vault appear in prerequisite order. Study status is your self-assessment, not proof of competence.',
  noGoals:'No goals yet. You can start without importing materials.',
  goalDescription:'What do you want to be able to do?', prerequisites:'Prerequisite goals',
  noPrerequisites:'No prerequisites', goalReady:'No unfinished prerequisites',
  goalBlocked:'Revisit first', goalStatus:'Your study status', ongoing:'In progress',
  edit:'Edit', deleteGoal:'Delete goal', deleteGoalConfirm:'Delete this goal and its prerequisite links? Other goals and materials will remain.',
  goalSource:'Material link', noGoalSource:'No material link', keepGoalSource:'Keep current material link',
  useGoalSource:'Link to the open material section',
  goal_title_required:'Enter a goal title (up to 200 characters).',
  goal_cycle:'These prerequisites would create a cycle. Choose different prerequisites.',
  goal_missing_prerequisite:'A prerequisite goal was not found in this vault.', invalid_goal:'Check the goal details.'
});

function goalsDialog() {
  const name = id => S.goals.find(g => g.id === id)?.title || '';
  modal(t('goals'), `<p>${t('goalIntro')}</p><button class="primary" id="newGoal">+ ${t('newGoal')}</button>
    ${S.goals.length ? S.goals.map(g => `<article class="list-card">
      <h3>${h(g.title)}</h3><span class="badge">${t(g.status)}</span>
      <p>${h(g.description)}</p><p>${t('prerequisites')}: ${g.prerequisites.length ? g.prerequisites.map(id=>h(name(id))).join(' · ') : t('noPrerequisites')}</p>
      <p class="notice">${g.unmet.length ? t('goalBlocked')+': '+g.unmet.map(id=>h(name(id))).join(' · ') : t('goalReady')}</p>
      <div class="buttons"><button data-edit-goal="${h(g.id)}">${t('edit')}</button>
      ${g.document_id ? `<button data-goal-source="${h(g.id)}">${t('revisit')}</button>` : ''}</div>
    </article>`).join('') : `<p>${t('noGoals')}</p>`}`, () => {
      $('#newGoal').onclick = () => goalEditor();
      document.querySelectorAll('[data-edit-goal]').forEach(b => b.onclick = () => goalEditor(S.goals.find(g=>g.id===b.dataset.editGoal)));
      document.querySelectorAll('[data-goal-source]').forEach(b => b.onclick = () => {
        const g = S.goals.find(g=>g.id===b.dataset.goalSource);
        closeModal(); S.course=''; S.view='lecture'; openDoc(g.document_id,g.page);
      });
    }, true);
}

function goalEditor(goal) {
  const candidates = S.goals.filter(g=>g.id!==goal?.id);
  modal(t(goal ? 'editGoal' : 'newGoal'), `<form id="goalForm" class="stack">
    <label>${t('title')}<input id="goalTitle" required maxlength="200" value="${h(goal?.title||'')}"></label>
    <label>${t('goalDescription')}<textarea id="goalDescription" maxlength="12000">${h(goal?.description||'')}</textarea></label>
    <label>${t('goalStatus')}<select id="goalStatus">${['waiting','ongoing','complete'].map(s=>`<option value="${s}" ${s===(goal?.status||'waiting')?'selected':''}>${t(s)}</option>`).join('')}</select></label>
    <fieldset class="goal-prerequisites"><legend>${t('prerequisites')}</legend>${candidates.length ? candidates.map(g=>`<label><input type="checkbox" name="prerequisite" value="${h(g.id)}" ${goal?.prerequisites.includes(g.id)?'checked':''}> ${h(g.title)}</label>`).join('') : `<p>${t('noPrerequisites')}</p>`}</fieldset>
    <label>${t('goalSource')}<select id="goalSource">
      ${goal?.document_id ? `<option value="keep">${t('keepGoalSource')}</option>` : ''}
      <option value="none">${t('noGoalSource')}</option>
      ${S.doc ? `<option value="current">${t('useGoalSource')}: ${h(contextLabel())}</option>` : ''}
    </select></label>
    <div class="buttons"><button class="primary" type="submit">${t('save')}</button>${goal ? `<button type="button" id="deleteGoal">${t('deleteGoal')}</button>` : ''}</div>
    </form>`, () => {
      $('#goalForm').onsubmit = async event => {
        event.preventDefault();
        const source = $('#goalSource').value;
        const data = {
          id:goal?.id, title:$('#goalTitle').value, description:$('#goalDescription').value,
          status:$('#goalStatus').value,
          prerequisites:[...document.querySelectorAll('[name="prerequisite"]:checked')].map(c=>c.value),
          document_id:source==='keep'?goal.document_id:source==='current'?S.doc.id:null,
          page:source==='keep'?goal.page:source==='current'?S.page:null
        };
        const button = $('#goalForm button[type="submit"]'); button.disabled=true;
        try { await api('/api/goals',data); S.goals=await api('/api/goals'); goalsDialog(); toast(t('saved')); }
        catch(e) { fail(e); button.disabled=false; }
      };
      $('#deleteGoal')?.addEventListener('click', async () => {
        if (!confirm(t('deleteGoalConfirm'))) return;
        try { await api('/api/goals/delete',{id:goal.id}); S.goals=await api('/api/goals'); goalsDialog(); }
        catch(e) { fail(e); }
      });
    });
}
