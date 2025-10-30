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
        const resp = await fetch(url, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: formData
        })

        if (!resp.ok) throw new Error('Network response not ok')
        const data = await resp.json()
        if (data && data.success) {
          // show token value and add to table
          alert('Token created: ' + data.token + '\nCopy it now — it will not be shown again.')
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
      if (!confirm('Revoke token?')) return
      el.disabled = true
      try {
        const resp = await fetch(`/tokens/${id}/revoke`, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
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
