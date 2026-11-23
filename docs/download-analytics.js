(() => {
  const eventName = 'vvfm_download_click';
  const waitMs = 250;

  function measure(event) {
    if (event.defaultPrevented || (event.type === 'auxclick' && event.button !== 1)) return;
    const link = event.target.closest?.('a[data-vvfm-download]');
    if (!link) return;
    const record = {
      event: eventName,
      download_placement: link.dataset.vvfmDownload,
      link_url: link.href
    };

    // Let modified clicks and new-tab links keep the browser's normal behavior.
    const layer = window.dataLayer = window.dataLayer || [];
    const waitForTag = Boolean(window.google_tag_manager?.['GTM-W75JZ67D']) &&
      event.type === 'click' && event.button === 0 && event.cancelable &&
      !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey &&
      (!link.target || link.target === '_self') && !link.hasAttribute('download');

    if (!waitForTag) {
      layer.push(record);
      return;
    }

    event.preventDefault();
    let navigated = false;
    let timer;
    const navigate = () => {
      if (navigated) return;
      navigated = true;
      window.clearTimeout(timer);
      window.location.assign(link.href);
    };
    // Never block access if GTM or the destination analytics tag fails.
    timer = window.setTimeout(navigate, waitMs);
    layer.push({ ...record, eventCallback: navigate, eventTimeout: waitMs });
  }

  document.addEventListener('click', measure);
  document.addEventListener('auxclick', measure);
})();
