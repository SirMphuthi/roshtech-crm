// users.js — small helper to AJAX-delete users (graceful fallback to form)
document.addEventListener('DOMContentLoaded', function () {
  document.body.addEventListener('click', async function (ev) {
    const el = ev.target
    if (!el) return
    // look for delete buttons inside the user list
    // Handle delete
    if (el.matches && (el.matches('.user-delete-btn') || el.closest('.user-delete-btn'))) {
      const btn = el.matches('.user-delete-btn') ? el : el.closest('.user-delete-btn')
      const userId = btn.getAttribute('data-user-id')
  if (!(window.uiConfirm ? await window.uiConfirm('Please confirm', 'Are you sure you want to delete this user?') : confirm('Are you sure you want to delete this user?'))) return
      btn.disabled = true
      try {
        const csrf = document.querySelector('meta[name="csrf-token"]')?.content
        const headers = {
          'X-Requested-With': 'XMLHttpRequest'
        }
        if (csrf) headers['X-CSRFToken'] = csrf

        const resp = await fetch(`/users/${userId}/delete`, {
          method: 'POST',
          headers
        })
        if (!resp.ok) throw new Error('Network error')
        const data = await resp.json().catch(() => null)
        // remove row on success; if server redirects instead, fallback to reload
        const row = btn.closest('tr')
        if (row) row.remove()
      } catch (err) {
        console.error(err)
        // fallback: submit the enclosing form if present
        const form = btn.closest('form')
        if (form) form.submit()
      }
    }

    // Handle open create modal
    if (el.matches && el.matches('#open-create-user')) {
      ev.preventDefault()
      openUserModal()
    }

    // Handle open edit modal
    if (el.matches && (el.matches('.user-edit-btn') || el.closest('.user-edit-btn'))) {
      ev.preventDefault()
      const btn = el.matches('.user-edit-btn') ? el : el.closest('.user-edit-btn')
      const userId = btn.getAttribute('data-user-id')
      openUserModal(userId)
    }

    // Handle make-owner button
    if (el.matches && el.matches('.make-owner-btn')) {
      ev.preventDefault()
      const btn = el
      const userId = btn.getAttribute('data-user-id')
      // ask for current user's password
      const pwd = prompt('To confirm making this user an owner, enter your password:')
      if (!pwd) return
      try {
        const form = new FormData()
        form.append('role', 'owner')
        form.append('confirm_password', pwd)
        const resp = await fetch(`/users/${userId}/role`, {method: 'POST', body: form, headers: {'X-Requested-With': 'XMLHttpRequest'}})
        if (!resp.ok) {
          const text = await resp.text()
          alert('Failed: ' + text)
          return
        }
        // reload to show updated role badge
        location.reload()
      } catch (err) {
        console.error(err)
        alert('Failed to make owner')
      }
    }
  })
})

// Open the user modal for create or edit. If userId is provided, load data.
async function openUserModal(userId) {
  // create modal markup if not present
  let modal = document.getElementById('user-modal')
  if (!modal) {
    modal = document.createElement('div')
    modal.id = 'user-modal'
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 hidden items-center justify-center'
    modal.innerHTML = `
      <div class="bg-white rounded-lg p-6 max-w-lg w-full">
        <h2 id="user-modal-title" class="text-lg font-semibold mb-2">User</h2>
        <form id="user-modal-form" class="space-y-3">
          <input type="hidden" name="user_id" id="user_id">
          <div>
            <label>First name</label>
            <input id="m_first_name" name="first_name" class="border rounded w-full px-2 py-1">
          </div>
          <div>
            <label>Last name</label>
            <input id="m_last_name" name="last_name" class="border rounded w-full px-2 py-1">
          </div>
          <div>
            <label>Email</label>
            <input id="m_email" name="email" class="border rounded w-full px-2 py-1">
          </div>
          <div>
            <label>Role</label>
            <select id="m_role" name="role" class="border rounded w-full px-2 py-1">
              <option value="user">User</option>
              <option value="admin">Admin</option>
              <option value="owner">Owner</option>
            </select>
          </div>
          <div class="text-right">
            <button id="m_cancel" class="bg-gray-300 px-3 py-2 rounded" type="button">Cancel</button>
            <button id="m_save" class="bg-blue-600 text-white px-3 py-2 rounded" type="submit">Save</button>
          </div>
        </form>
      </div>`
    document.body.appendChild(modal)

    // event handlers
    modal.querySelector('#m_cancel').addEventListener('click', function () {
      modal.classList.add('hidden')
      modal.classList.remove('flex')
    })
    modal.querySelector('#user-modal-form').addEventListener('submit', async function (ev) {
      ev.preventDefault()
      const form = ev.target
      const formData = new FormData(form)
      const userId = formData.get('user_id')
      const url = userId ? `/users/${userId}/edit` : '/users/create'
      const csrf = document.querySelector('meta[name="csrf-token"]')?.content
      const headers = {'X-Requested-With': 'XMLHttpRequest'}
      if (csrf) headers['X-CSRFToken'] = csrf
      try {
        const resp = await fetch(url, {method: 'POST', headers, body: formData})
        if (!resp.ok) throw new Error('Network error')
        const data = await resp.json()
        if (data && data.success) {
          // update or prepend row
          updateUserRow(data)
          modal.classList.add('hidden')
          modal.classList.remove('flex')
        } else {
          alert(data && data.error ? data.error : 'Failed')
        }
      } catch (err) {
        console.error(err)
        // fallback to submit form normally
        form.submit()
      }
    })
  }

  // show modal
  modal.classList.remove('hidden')
  modal.classList.add('flex')

  if (userId) {
    // load user data
    try {
      const resp = await fetch(`/users/${userId}/json`, {headers: {'X-Requested-With': 'XMLHttpRequest'}})
      if (!resp.ok) throw new Error('Failed to fetch')
      const data = await resp.json()
      document.getElementById('user_id').value = data.id
      document.getElementById('m_first_name').value = data.first_name
      document.getElementById('m_last_name').value = data.last_name
      document.getElementById('m_email').value = data.email
      document.getElementById('m_role').value = data.role
      document.getElementById('user-modal-title').textContent = 'Edit User'
    } catch (err) {
      console.error(err)
    }
  } else {
    document.getElementById('user_id').value = ''
    document.getElementById('m_first_name').value = ''
    document.getElementById('m_last_name').value = ''
    document.getElementById('m_email').value = ''
    document.getElementById('m_role').value = 'user'
    document.getElementById('user-modal-title').textContent = 'Create User'
  }
}

function updateUserRow(data) {
  // find existing row by data.id; if not found, prepend new row
  const rows = document.querySelectorAll('table tbody tr')
  let found = false
  rows.forEach(r => {
    const idCell = r.querySelector('td')
    if (idCell && idCell.textContent.trim() == data.id) {
      // update cells
      r.querySelectorAll('td')[1].textContent = data.email
      r.querySelectorAll('td')[0].textContent = data.first_name + ' ' + data.last_name
      r.querySelectorAll('td')[2].textContent = data.role
      found = true
    }
  })
    if (!found) {
    const tbody = document.querySelector('table tbody')
    if (!tbody) return
    const tr = document.createElement('tr')
    tr.className = 'border-t'
    tr.innerHTML = `\
      <td class="py-3 px-6 text-left">${data.first_name} ${data.last_name}</td>\
      <td class="py-3 px-6 text-left">${data.email}</td>\
      <td class="py-3 px-6 text-center"><span class="bg-blue-200 text-blue-600 py-1 px-3 rounded-full text-xs">${data.role}</span></td>\
      <td class="py-3 px-6 text-center">\
        <div class="flex item-center justify-center">\
          <a href="#" class="user-edit-btn w-4 mr-4 transform hover:text-blue-500 hover:scale-110" data-user-id="${data.id}">Edit</a>\
          <form action="/users/${data.id}/delete" method="POST" class="inline">\
            <button type="button" data-user-id="${data.id}" class="user-delete-btn w-4 transform hover:text-red-500 hover:scale-110" data-confirm="Are you sure you want to delete this user?">Delete</button>\
          </form>\
        </div>\
      </td>`
    tbody.prepend(tr)
  }
}
