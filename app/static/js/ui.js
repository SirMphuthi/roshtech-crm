// Simple UI utilities: reusable confirmation modal
document.addEventListener('DOMContentLoaded', function () {
  const modal = document.getElementById('confirmModal')
  if (!modal) return

  const titleEl = document.getElementById('confirmModalTitle')
  const bodyEl = document.getElementById('confirmModalBody')
  const okBtn = document.getElementById('confirmOk')
  const cancelBtn = document.getElementById('confirmCancel')

  let resolveFn = null

  function openModal(title, body) {
    titleEl.textContent = title || 'Confirm'
    bodyEl.textContent = body || 'Are you sure?'
    modal.classList.remove('hidden')
    return new Promise((resolve) => {
      resolveFn = resolve
    })
  }

  function closeModal(result) {
    modal.classList.add('hidden')
    if (resolveFn) {
      resolveFn(result)
      resolveFn = null
    }
  }

  okBtn.addEventListener('click', function () { closeModal(true) })
  cancelBtn.addEventListener('click', function () { closeModal(false) })

  // Delegate click handlers for elements with data-confirm attribute
  document.body.addEventListener('click', function (e) {
    const el = e.target.closest('[data-confirm]')
    if (!el) return
    e.preventDefault()
    const title = el.getAttribute('data-confirm-title') || 'Please confirm'
    const body = el.getAttribute('data-confirm') || 'Are you sure?'
    openModal(title, body).then(function (ok) {
      if (!ok) return
      // If the element is a form submit button, submit the enclosing form
      if (el.tagName === 'BUTTON' && el.type === 'submit') {
        const form = el.closest('form')
        if (form) form.submit()
      } else if (el.tagName === 'A' && el.href) {
        window.location = el.href
      } else {
        // fallback: trigger click on element's target if provided
        const targetSelector = el.getAttribute('data-confirm-target')
        if (targetSelector) {
          const target = document.querySelector(targetSelector)
          if (target) target.click()
        }
      }
    })
  })
  // expose programmatic API
  window.uiConfirm = openModal
})
