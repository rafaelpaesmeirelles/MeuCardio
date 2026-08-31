export type CardiologySpaceSceneId =
  | "consultorio" | "hospital" | "ensino" | "pesquisa" | "gestao"
  | "descobrir" | "evidencias" | "aprender" | "ensinar" | "produzir";

export default function CardiologySpaceScene({ space }: { space: CardiologySpaceSceneId }) {
  return (
    <svg className="spaces-door__scene" viewBox="0 0 220 150" focusable="false" aria-hidden="true">
      <g className="spaces-door__architecture">
        <path d="M12 140 34 24h152l22 116M34 24l18 17h116l18-17M52 41v99m116-99v99M12 140h196" />
        <path d="M52 41 12 140m156-99 40 99M82 41l-8 99m64-99 8 99M19 119h182" opacity=".42" />
        <path d="M74 18h72M83 25h54" className="spaces-door__ceiling" />
      </g>
      {space === "consultorio" && <g className="spaces-door__furniture"><path d="M69 92h75l10 10H60l9-10Zm-2 10v25m79-25v25M86 91V70h39v21M92 76h27"/><path d="M36 105h22v22H36zm6 0V94h19M161 81h29v46h-29zM168 89h15m-15 8h15"/><path d="M151 69c4-7 10-11 18-12m-12 21c-1-8 2-14 8-19m-8 19h19v4h-19Z"/><circle cx="105" cy="82" r="3"/></g>}
      {space === "hospital" && <g className="spaces-door__furniture"><path d="M48 103h87l15 11H39l9-11Zm1 11v13m94-13v13M62 102V88h55l16 15M64 94h23"/><path d="M157 74h28v53h-28zM164 83h14m-7-7v14M158 101h26"/><path d="M36 69h31v25H36zm5 5h21v15H41m11 5v9M34 103h36"/><path d="M91 46v33m-15-22h30M87 65h8" className="spaces-door__lit"/></g>}
      {space === "ensino" && <g className="spaces-door__furniture"><path d="M74 55h73v43H74zM81 62h59v29H81M110 98v12m-15 0h30"/><path d="M35 117h38l5 10H30l5-10Zm7-18h23v18H42zm48 18h38l5 10H85l5-10Zm7-18h23v18H97zm48 18h38l5 10h-48l5-10Zm7-18h23v18h-23z"/><path d="M85 72h19m-19 7h43m-43 7h32" className="spaces-door__lit"/></g>}
      {space === "pesquisa" && <g className="spaces-door__furniture"><path d="M50 102h120l8 12H42l8-12Zm3 12v13m114-13v13"/><path d="M73 64h16v38H67l6-38Zm4 0v-8h9v8M72 83h18M109 71h21v31h-27l6-31Zm3 8h15"/><path d="M143 97V64m-10 0h28m-20-8c0-6 4-11 10-11s10 5 10 11v8h-20v-8Z"/><path d="M33 55h29v35H33zM39 62h17m-17 7h11m-11 7h15" className="spaces-door__lit"/></g>}
      {space === "gestao" && <g className="spaces-door__furniture"><path d="M74 99h88l10 14H65l9-14Zm4 14v14m80-14v14M95 99V79h46v20"/><path d="M40 58h33v69H40zM47 110V94h6v16m5 0V82h6v28"/><path d="M91 51h77v39H91zM99 81V68h8v13m8 0V59h8v22m8 0V70h8v11m8 0V62h8v19" className="spaces-door__lit"/><path d="M99 59c10-9 19-3 27-10 7-6 15-5 26-11"/></g>}
      {space === "descobrir" && <g className="spaces-door__furniture"><circle cx="96" cy="77" r="26"/><path d="m115 96 24 24M82 66c9-9 22-9 31 0M82 77h32M86 88c8 6 18 6 26 0"/><path d="M43 56h25v62H43zM48 65h15m-15 9h15m-15 9h10M154 52h25v66h-25zM159 62h15m-15 9h15m-15 9h10" className="spaces-door__lit"/></g>}
      {space === "evidencias" && <g className="spaces-door__furniture"><path d="M48 51h50v67H48zM58 63h29m-29 11h29m-29 11h22M116 61h55v57h-55zM126 73h34m-34 11h34m-34 11h25"/><path d="m78 105 7 7 18-23M143 103l8-18 8 18m-12-7h9" className="spaces-door__lit"/></g>}
      {space === "aprender" && <g className="spaces-door__furniture"><path d="m52 65 58-26 58 26-58 27Z"/><path d="M72 82v23c21 13 55 13 76 0V82M161 69v38"/><circle cx="161" cy="112" r="5" className="spaces-door__lit"/><path d="M63 122h94"/></g>}
      {space === "ensinar" && <g className="spaces-door__furniture"><path d="M48 48h124v66H48zM58 59h104v44H58zM109 114v13m-28 0h58"/><path d="M70 88V75h13v13m11 0V65h13v23m11 0V70h13v18m11 0V59h13v29" className="spaces-door__lit"/></g>}
      {space === "produzir" && <g className="spaces-door__furniture"><path d="M54 49h71l21 21v56H54zM125 49v22h21M68 82h63M68 94h63M68 106h44"/><path d="m149 106 21-21 9 9-21 21-14 5Z" className="spaces-door__lit"/><path d="M156 88l9 9"/></g>}
    </svg>
  );
}
