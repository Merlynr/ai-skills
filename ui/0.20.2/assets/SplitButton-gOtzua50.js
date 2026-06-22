import{r as e}from"./rolldown-runtime-Dw2cE7zH.js";import{i as t,r as n,t as r}from"./vendor-react-FFrd4RqC.js";import{t as i}from"./Spinner-BNr16s5C.js";import{I as a}from"./index-CPjxJ6a2.js";var o=e(t(),1),s=e(n(),1),c=r(),l={primary:`bg-pencil text-paper border-2 border-pencil`,secondary:`bg-transparent text-pencil border-2 border-muted-dark hover:border-pencil`},u={primary:`hover:bg-paper/10`,secondary:`hover:bg-muted/30`},d={primary:`bg-paper/25`,secondary:`bg-muted-dark`},f={primary:`bg-pencil text-paper`,secondary:`bg-surface/95 text-pencil`},p={primary:{border:`2px solid var(--color-pencil)`,boxShadow:`0 8px 24px rgba(0, 0, 0, 0.12), 0 2px 6px rgba(0, 0, 0, 0.06)`},secondary:{border:`1px solid var(--color-muted-dark)`,boxShadow:`0 8px 24px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.04)`}},m={primary:`hover:bg-paper/15`,secondary:`hover:bg-muted/50`},h={sm:`px-3 py-1.5 text-sm`,md:`px-5 py-2.5 text-sm`,lg:`px-6 py-3 text-base`},g={sm:`px-1.5`,md:`px-2`,lg:`px-2.5`},_={sm:`text-sm py-1`,md:`text-sm py-1`,lg:`text-base py-1.5`},v={sm:`px-3.5 py-2`,md:`px-4 py-2.5`,lg:`px-4 py-3`};function y({anchorRef:e,align:t,variant:n,size:r,items:i,onClose:a}){let l=(0,o.useRef)(null),[u,d]=(0,o.useState)(null),[h,g]=(0,o.useState)(null);return(0,o.useEffect)(()=>{if(!e.current)return;let n=e.current.getBoundingClientRect();d({top:n.bottom+6,left:t===`right`?void 0:n.left,right:t===`right`?window.innerWidth-n.right:void 0});let r=()=>a();return window.addEventListener(`scroll`,r,!0),window.addEventListener(`resize`,r),()=>{window.removeEventListener(`scroll`,r,!0),window.removeEventListener(`resize`,r)}},[e,t,a]),(0,o.useEffect)(()=>{let t=t=>{let n=t.target;l.current&&!l.current.contains(n)&&e.current&&!e.current.contains(n)&&a()};return document.addEventListener(`mousedown`,t),()=>document.removeEventListener(`mousedown`,t)},[e,a]),(0,o.useEffect)(()=>{let e=e=>{e.key===`Escape`&&a()};return document.addEventListener(`keydown`,e),()=>document.removeEventListener(`keydown`,e)},[a]),u?(0,s.createPortal)((0,c.jsx)(`div`,{ref:l,className:`
        fixed ss-split-menu min-w-[160px]
        ${f[n]}
        ${_[r]}
        overflow-hidden
      `,style:{zIndex:99999,top:u.top,left:u.left,right:u.right,borderRadius:`var(--radius-lg)`,...p[n]},role:`menu`,children:i.map((e,t)=>{let i=h===t;return(0,c.jsxs)(`button`,{className:`
              ss-split-menu-item
              w-full flex items-center gap-2.5 ${v[r]}
              text-left cursor-pointer font-medium
              ${i?n===`primary`?`bg-paper/10 text-warning`:`bg-warning/10 text-warning`:m[n]}
            `,role:`menuitem`,onClick:()=>{if(e.confirm&&!i){g(t);return}a(),e.onClick()},children:[e.icon&&(0,c.jsx)(`span`,{className:`ss-split-menu-icon shrink-0`,children:e.icon}),i?e.confirmLabel??`Are you sure?`:e.label]},t)})}),document.body):null}function b({children:e,onClick:t,items:n,variant:r=`primary`,size:s=`md`,loading:f=!1,disabled:p=!1,className:m=``,dropdownAlign:_=`left`}){let[v,b]=(0,o.useState)(!1),x=(0,o.useRef)(null),S=p||f,C=(0,o.useCallback)(()=>b(!1),[]);return(0,c.jsxs)(`div`,{className:`inline-flex ${m}`,children:[(0,c.jsxs)(`div`,{ref:x,className:`
          ss-btn
          inline-flex items-center
          rounded-[var(--radius-btn)] overflow-hidden
          transition-all duration-150
          active:scale-[0.98]
          ${l[r]}
          ${S?`opacity-50 pointer-events-none`:``}
        `,children:[(0,c.jsxs)(`button`,{className:`
            inline-flex items-center justify-center gap-2
            font-medium cursor-pointer
            transition-colors duration-150
            focus-visible:ring-2 focus-visible:ring-pencil/20 focus-visible:ring-offset-2
            ${u[r]}
            ${h[s]}
          `,onClick:t,disabled:S,children:[f&&(0,c.jsx)(i,{size:`sm`,className:`text-current`}),e]}),(0,c.jsx)(`div`,{className:`w-px self-stretch ${d[r]}`}),(0,c.jsx)(`button`,{className:`
            inline-flex items-center justify-center self-stretch
            cursor-pointer
            transition-colors duration-150
            focus-visible:ring-2 focus-visible:ring-pencil/20 focus-visible:ring-offset-2
            ${u[r]}
            ${g[s]}
          `,onClick:()=>b(e=>!e),disabled:S,"aria-haspopup":`true`,"aria-expanded":v,"aria-label":`More options`,children:(0,c.jsx)(a,{size:s===`lg`?18:14,strokeWidth:2.5,className:`transition-transform duration-150 ${v?`rotate-180`:``}`})})]}),v&&(0,c.jsx)(y,{anchorRef:x,align:_,variant:r,size:s,items:n,onClose:C})]})}export{b as t};