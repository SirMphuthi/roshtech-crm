// tokens.js — small helper to create and revoke tokens via AJAX

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('token-create-form')
  const btn = document.getElementById('token-create-btn')

  if (form) {
    form.addEventListener('submit', async function (ev) {
      ev.preventDefault()
      btn.disabled = true
      btn.textContent = 'Creating...'

      const url = form.action
      const formData = new FormData(form)

      try {
        // include CSRF header if available
        const csrf = document.querySelector('meta[name="csrf-token"]')?.content
        const headers = {
          'X-Requested-With': 'XMLHttpRequest'
        }
        if (csrf) headers['X-CSRFToken'] = csrf

        const resp = await fetch(url, {
          method: 'POST',
          headers,
          body: formData
        })

        if (!resp.ok) throw new Error('Network response not ok')
        const data = await resp.json()
          if (data && data.success) {
          // show token value in modal and add to table
          const modal = document.getElementById('token-modal')
          const tokenValueEl = document.getElementById('token-value')
          const copyBtn = document.getElementById('token-copy-btn')
          const closeBtn = document.getElementById('token-close-btn')
          if (modal && tokenValueEl) {
            tokenValueEl.textContent = data.token
            modal.classList.remove('hidden')
            modal.classList.add('flex')
            // copy handler
            copyBtn && copyBtn.addEventListener('click', function () {
              navigator.clipboard && navigator.clipboard.writeText(data.token)
              copyBtn.textContent = 'Copied'
            })
            closeBtn && closeBtn.addEventListener('click', function () {
              modal.classList.add('hidden')
              modal.classList.remove('flex')
            })
          }
          // prepend new row to table
          const tbody = document.querySelector('table tbody')
          if (tbody) {
            const tr = document.createElement('tr')
            tr.className = 'border-t'
            const created = new Date(data.created_at).toISOString().slice(0,16).replace('T',' ')
            const expires = data.expires_at ? (new Date(data.expires_at).toISOString().slice(0,16).replace('T',' ')) : '-'
            tr.innerHTML = `\
              <td class="p-2">${data.id}</td>\
              <td class="p-2">${data.user_email}</td>\
              <td class="p-2 font-mono">${data.token_prefix}</td>\
              <td class="p-2">${created}</td>\
              <td class="p-2">${expires}</td>\
              <td class="p-2">No</td>\
              <td class="p-2"><button class="bg-red-500 text-white px-2 py-1 rounded revoke-btn" data-token-id="${data.id}">Revoke</button></td>`
            tbody.prepend(tr)
          }
          form.reset()
        } else {
          alert('Failed to create token')
        }
      } catch (err) {
        console.error(err)
        alert('Error creating token')
      } finally {
        btn.disabled = false
        btn.textContent = 'Create Token'
      }
    })
  }

  // Delegate revoke buttons
  document.body.addEventListener('click', async function (ev) {
    const el = ev.target
    if (el && el.classList && el.classList.contains('revoke-btn')) {
      const id = el.getAttribute('data-token-id')
      const confirmed = window.uiConfirm ? await window.uiConfirm('Please confirm', 'Revoke token?') : confirm('Revoke token?')
      if (!confirmed) return
      el.disabled = true
      try {
        const csrf = document.querySelector('meta[name="csrf-token"]')?.content
        const headers = {
          'X-Requested-With': 'XMLHttpRequest'
        }
        if (csrf) headers['X-CSRFToken'] = csrf

        const resp = await fetch(`/tokens/${id}/revoke`, {
          method: 'POST',
          headers
        })
        if (!resp.ok) throw new Error('Network response not ok')
        const data = await resp.json()
        if (data && data.success) {
          // Mark row revoked (find parent tr)
          const row = el.closest('tr')
          if (row) {
            row.querySelectorAll('td')[5].textContent = 'Yes'
            el.remove()
          }
        } else {
          alert('Failed to revoke token')
          el.disabled = false
        }
      } catch (err) {
        console.error(err)
        alert('Error revoking token')
        el.disabled = false
      }
    }
  })
})
