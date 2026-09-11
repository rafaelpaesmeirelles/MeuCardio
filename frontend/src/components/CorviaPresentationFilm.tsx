import { useEffect, useRef, useState } from "react";
import Icone from "./Icone";

const FILM_ROOT = "/media/corvia-apresentacao-20260911";

/** Optional presentation: never starts playback or completes onboarding for the user. */
export default function CorviaPresentationFilm() {
  const [open, setOpen] = useState(false);
  const [failed, setFailed] = useState(false);
  const trigger = useRef<HTMLButtonElement>(null);
  const dialog = useRef<HTMLDialogElement>(null);
  const video = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (!open) return;
    const current = dialog.current;
    current?.showModal();
    return () => {
      current?.querySelector("video")?.pause();
      current?.close();
      trigger.current?.focus({ preventScroll: true });
    };
  }, [open]);

  return <>
    <button ref={trigger} type="button" className="cst-at__film-trigger" aria-haspopup="dialog" onClick={() => { setFailed(false); setOpen(true); }}>
      <Icone nome="camera" /><span>Veja o CorVIA em movimento<small>Filme de apresentação · 1 min 12 s</small></span><Icone nome="seta" />
    </button>
    {open && <dialog ref={dialog} className="cst-at__film-dialog" aria-labelledby="corvia-film-title" onCancel={() => setOpen(false)} onClose={() => setOpen(false)}>
      <header><div><p>CorVIA · Cardiology Spaces</p><h2 id="corvia-film-title">Cinco espaços. Uma só cardiologia.</h2></div><button type="button" aria-label="Fechar filme" onClick={() => setOpen(false)}><Icone nome="fechar" /></button></header>
      <video ref={video} controls playsInline preload="none" poster={`${FILM_ROOT}.jpg`} onError={() => setFailed(true)} aria-label="Filme de apresentação do CorVIA com telas do sistema e trilha instrumental">
        <source src={`${FILM_ROOT}.mp4`} type="video/mp4" />
        <track kind="captions" src={`${FILM_ROOT}.vtt`} srcLang="pt-BR" label="Português" />
        Seu navegador não oferece reprodução de vídeo. Use a opção de download abaixo.
      </video>
      {failed && <p className="cst-at__film-error" role="alert">Não foi possível carregar o filme. Você pode tentar baixá-lo para assistir no seu dispositivo.</p>}
      <footer><p>Ative o som para ouvir a trilha. As telas assistenciais apresentadas usam dados demonstrativos, sem identificar pacientes.</p><a href={`${FILM_ROOT}.mp4`} download="CorVIA-Cardiology-Spaces.mp4">Baixar vídeo MP4 <Icone nome="seta" /></a></footer>
    </dialog>}
  </>;
}
