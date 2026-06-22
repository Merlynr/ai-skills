import{r as e}from"./rolldown-runtime-Dw2cE7zH.js";import{i as t,t as n}from"./vendor-react-FFrd4RqC.js";import{d as r,f as i}from"./Spinner-BNr16s5C.js";import{t as a}from"./minus-BBMyR2gL.js";import{I as o,L as s}from"./index-CPjxJ6a2.js";var c=e(t(),1),l=n(),u={sm:{box:`w-4 h-4`,icon:12,text:`text-sm`},md:{box:`w-5 h-5`,icon:14,text:`text-base`}};function d({label:e,checked:t,onChange:n,className:i=``,indeterminate:o=!1,disabled:d=!1,size:f=`md`}){let p=(0,c.useId)(),m=u[f];return(0,l.jsxs)(`label`,{htmlFor:p,className:`
        inline-flex items-center gap-2 select-none
        ${d?`opacity-50 cursor-not-allowed`:`cursor-pointer`}
        ${i}
      `,children:[(0,l.jsx)(`input`,{id:p,type:`checkbox`,checked:t,onChange:e=>!d&&n(e.target.checked),disabled:d,className:`sr-only`}),(0,l.jsx)(`span`,{className:`
          ${m.box} flex items-center justify-center border transition-all duration-150
          ${d?``:`active:scale-95`}
          focus-visible:ring-2 focus-visible:ring-blue/30 focus-visible:ring-offset-1
          ${t||o?`bg-blue border-blue`:`bg-surface border-muted-dark hover:border-pencil-light`}
        `,style:{borderRadius:r.sm},children:o?(0,l.jsx)(a,{size:m.icon,strokeWidth:3,className:`text-white`}):t?(0,l.jsx)(s,{size:m.icon,strokeWidth:3,className:`text-white`}):null}),(0,l.jsx)(`span`,{className:`${m.text} text-pencil`,children:e})]})}var f={sm:`px-3 py-1.5 text-xs`,md:`px-4 py-2 text-sm`};function p({label:e,value:t,onChange:n,options:a,className:u=``,size:d=`md`,disabled:p=!1}){let[m,h]=(0,c.useState)(!1),[g,_]=(0,c.useState)(-1),[v,y]=(0,c.useState)(!1),[b,x]=(0,c.useState)(!1),S=(0,c.useRef)(null),C=(0,c.useRef)(null),w=a.find(e=>e.value===t)?.label??t;(0,c.useEffect)(()=>{if(!m)return;let e=e=>{S.current&&!S.current.contains(e.target)&&h(!1)};return document.addEventListener(`mousedown`,e),()=>document.removeEventListener(`mousedown`,e)},[m]),(0,c.useLayoutEffect)(()=>{if(!m||!S.current)return;let e=S.current.getBoundingClientRect(),t=Math.min(a.length*48,256);y(window.innerHeight-e.bottom<t+8&&e.top>t),x(window.innerWidth-e.left<240)},[m,a.length]),(0,c.useEffect)(()=>{if(!m||g<0||!C.current)return;let e=C.current.children;e[g]&&e[g].scrollIntoView({block:`nearest`})},[m,g]);let T=(0,c.useCallback)(e=>{n(e),h(!1)},[n]),E=(0,c.useCallback)(e=>{switch(e.key){case`ArrowDown`:e.preventDefault(),m?_(e=>Math.min(e+1,a.length-1)):(h(!0),_(0));break;case`ArrowUp`:e.preventDefault(),m&&_(e=>Math.max(e-1,0));break;case`Enter`:case` `:e.preventDefault(),m&&g>=0?T(a[g].value):(h(!0),_(Math.max(0,a.findIndex(e=>e.value===t))));break;case`Escape`:h(!1);break}},[m,g,a,t,T]);return(0,l.jsxs)(`div`,{ref:S,className:`relative ${u}`,children:[e&&(0,l.jsx)(`label`,{className:`block text-xs font-medium text-pencil-light mb-1`,children:e}),(0,l.jsxs)(`button`,{type:`button`,disabled:p,onClick:()=>{p||(h(!m),_(a.findIndex(e=>e.value===t)))},onKeyDown:E,className:`
          ss-select
          w-full bg-surface border-2 text-pencil text-left
          flex items-center justify-between gap-2
          focus:outline-none focus:border-pencil
          transition-all duration-150
          rounded-[var(--radius-sm)]
          ${p?`opacity-50 cursor-not-allowed`:`cursor-pointer`}
          ${f[d]}
          ${m?`border-pencil`:`border-muted hover:border-muted-dark`}
        `,role:`combobox`,"aria-expanded":m,"aria-haspopup":`listbox`,children:[(0,l.jsx)(`span`,{className:`truncate`,children:w}),(0,l.jsx)(o,{size:d===`sm`?13:15,strokeWidth:2,className:`shrink-0 text-muted-dark transition-transform duration-200 ${m?`rotate-180`:``}`})]}),m&&(0,l.jsx)(`ul`,{ref:C,role:`listbox`,className:`
            absolute z-50 min-w-full bg-surface border-2 border-muted overflow-auto py-1 animate-dropdown-in
            ${v?`bottom-full mb-1`:`top-full mt-1`}
            ${b?`right-0`:`left-0`}
            ${d===`sm`?`text-xs`:`text-sm`}
          `,style:{borderRadius:r.md,boxShadow:i.lg,maxHeight:`16rem`},children:a.map((e,n)=>{let r=e.value===t,i=n===g;return(0,l.jsxs)(`li`,{role:`option`,"aria-selected":r,className:`
                  ${d===`sm`?`px-3 py-1.5`:`px-3.5 py-2`} cursor-pointer flex items-center gap-2 transition-colors duration-100
                  ${i?`bg-muted/60`:``}
                  ${r?`text-pencil`:`text-pencil-light`}
                  hover:bg-muted/60
                `,onMouseEnter:()=>_(n),onMouseDown:t=>{t.preventDefault(),T(e.value)},children:[(0,l.jsx)(`span`,{className:`w-4 shrink-0 flex items-center justify-center`,children:r&&(0,l.jsx)(s,{size:d===`sm`?12:14,strokeWidth:2.5,className:`text-pencil`})}),(0,l.jsxs)(`span`,{className:`flex-1 min-w-0`,children:[(0,l.jsx)(`span`,{className:`block truncate ${r?`font-medium`:``}`,children:e.label}),e.description&&(0,l.jsx)(`span`,{className:`block text-xs text-pencil-light/60 mt-0.5 truncate`,children:e.description})]})]},e.value)})})]})}function m({label:e,className:t=``,style:n,id:r,size:i=`md`,...a}){let o=(0,c.useId)(),s=r??o,u=i===`sm`?`px-3 py-1.5`:`px-4 py-2.5`,d=i===`sm`?`0.85rem`:`1rem`;return(0,l.jsxs)(`div`,{children:[e&&(0,l.jsx)(`label`,{htmlFor:s,className:`block text-base text-pencil-light mb-1`,children:e}),(0,l.jsx)(`input`,{id:s,className:`
          ss-input
          w-full ${u} bg-surface border-2 border-muted text-pencil
          placeholder:text-muted-dark
          hover:border-muted-dark
          focus:outline-none focus:border-pencil
          transition-all
          rounded-[var(--radius-md)]
          ${t}
        `,style:{fontSize:d,...n},...a})]})}function h({label:e,className:t=``,style:n,id:r,size:i=`md`,...a}){let o=(0,c.useId)(),s=r??o,u=i===`sm`?`px-3 py-1.5`:`px-4 py-3`,d=i===`sm`?`0.85rem`:`0.95rem`;return(0,l.jsxs)(`div`,{children:[e&&(0,l.jsx)(`label`,{htmlFor:s,className:`block text-base text-pencil-light mb-1`,children:e}),(0,l.jsx)(`textarea`,{id:s,className:`
          ss-input
          w-full ${u} bg-surface border-2 border-muted text-pencil
          placeholder:text-muted-dark
          hover:border-muted-dark
          focus:outline-none focus:border-pencil
          transition-all resize-y
          rounded-[var(--radius-md)]
          ${t}
        `,style:{fontSize:d,...n},...a})]})}export{d as i,h as n,p as r,m as t};