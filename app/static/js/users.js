// users.js — small helper to AJAX-delete users (graceful fallback to form)
document.addEventListener('DOMContentLoaded', function () {
  document.body.addEventListener('click', async function (ev) {
    const el = ev.target
    if (!el) return
    // look for delete buttons inside the user list
    if (el.matches && (el.matches('.user-delete-btn') || el.closest('.user-delete-btn'))) {
      const btn = el.matches('.user-delete-btn') ? el : el.closest('.user-delete-btn')
      const userId = btn.getAttribute('data-user-id')
      if (!confirm('Are you sure you want to delete this user?')) return
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
  })
})
