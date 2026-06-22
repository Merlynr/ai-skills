import{t as e}from"./vendor-react-FFrd4RqC.js";import{t}from"./Spinner-BNr16s5C.js";var n=e(),r={primary:`bg-pencil text-paper border-2 border-pencil hover:bg-pencil/85`,secondary:`bg-transparent text-pencil border-2 border-muted-dark hover:bg-muted/30 hover:border-pencil hover:shadow-sm`,danger:`bg-transparent text-danger border-2 border-danger hover:bg-danger hover:text-white`,warning:`bg-transparent text-warning border-2 border-warning hover:bg-warning hover:text-white`,ghost:`bg-transparent text-pencil-light hover:text-pencil hover:bg-muted/30`,link:`bg-transparent text-pencil-light hover:text-pencil hover:underline border-none`},i={xs:`px-2 py-1 text-xs`,sm:`px-3 py-1.5 text-sm`,md:`px-5 py-2.5 text-sm`,lg:`px-6 py-3 text-base`};function a({children:e,variant:a=`primary`,size:o=`md`,className:s=``,disabled:c,loading:l=!1,style:u,ref:d,...f}){let p=a===`link`,m=a===`ghost`||a===`link`,h=c||l;return(0,n.jsxs)(`button`,{ref:d,className:`
        ${m?``:`ss-btn`}
        inline-flex items-center justify-center gap-2
        font-medium
        transition-all duration-150 cursor-pointer
        active:scale-[0.98]
        focus-visible:ring-2 focus-visible:ring-pencil/20 focus-visible:ring-offset-2
        disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100
        ${r[a]}
        ${p?`text-sm p-0`:`${i[o]} rounded-[var(--radius-btn)]`}
        ${s}
      `,style:u,disabled:h,...f,children:[l&&(0,n.jsx)(t,{size:`sm`,className:`text-current`}),e]})}export{a as t};