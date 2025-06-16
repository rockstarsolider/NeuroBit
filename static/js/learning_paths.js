/* ================================================================
   PATH-DISCOVERY QUIZ – FINAL VERSION (2025-06-09)
   ----------------------------------------------------------------
   • 5-step form with live validation
   • real 0-100 % progress bar
   • single “Next/Finish” button
   • theme-aware radar chart (Chart.js)
==================================================================*/
// import Chart from 'chart.js/auto';

document.addEventListener("DOMContentLoaded", () => {

    /* ---------- DOM refs ---------------------------------------- */
    const form      = document.getElementById("pdq-form");
    const steps     = form.querySelectorAll("[data-step]");
    const bar       = document.querySelector(".pdq-bar");
    const prevBtn   = form.querySelector(".pdq-prev");
    const nextBtn   = form.querySelector(".pdq-next");
    const resultBox = document.getElementById("pdq-result");
    const canvas    = document.getElementById("pdq-chart");
    const ctx       = canvas.getContext("2d");
    const primaryEl = document.getElementById("pdq-primary");
    const secondEl  = document.getElementById("pdq-secondary");
    const scrollBtn = document.getElementById("pdq-scroll-cards");
  
    /* ---------- constants --------------------------------------- */
    const PATHS = {F:"frontend_title", B:"backend_title", AI:"ai_title",
                   G:"design_title",  GM:"game_title"};
  
    let step = 0;               // section index
    let chart = null;
    let highlighted = [];       // cards outlined
  
    /* =============================================================
       NAVIGATION
    ============================================================= */
    function pct(i){ return (i / (steps.length - 1)) * 100; } // 0..4 ➜ 0..100
  
    function showStep(i){
      steps.forEach((fs,idx)=>fs.style.display = idx===i?"block":"none");
      prevBtn.disabled = (i===0);
  
      const isFinal = (i===steps.length-1);
      nextBtn.textContent   = translations[currentLang][isFinal?"pdq_finish":"pdq_next"];
      nextBtn.dataset.finish = isFinal?"1":"";
  
      bar.style.width = pct(i)+"%";
    }
  
    function valid(fs){
      for(const q of fs.querySelectorAll(".pdq-q")){
        const inp = q.querySelector("input");
        if(inp.required && !form[inp.name].value){
          q.classList.add("pdq-error");
          q.scrollIntoView({behavior:"smooth",block:"center"});
          return false;
        }
        q.classList.remove("pdq-error");
      }
      return true;
    }
  
    prevBtn.onclick = () => { step=Math.max(0,--step); showStep(step); };
  
    nextBtn.onclick = () => {
      if(!valid(steps[step])) return;
  
      if(nextBtn.dataset.finish){ form.requestSubmit(); return; }
  
      step=Math.min(steps.length-1,++step); showStep(step);
    };
  
    /* =============================================================
       CHART UTILITIES
    ============================================================= */
    function hex2rgba(hex,a=0.25){
      const n=parseInt(hex.slice(1),16);
      return `rgba(${n>>16&255},${n>>8&255},${n&255},${a})`;
    }
    function themeColors(){
      const css=getComputedStyle(document.documentElement);
      return{
        accent:(css.getPropertyValue("--accent")||"#00e0b9").trim(),
        text  :(css.getPropertyValue("--text")  ||"#e2e8f0").trim(),
        grid  :(css.getPropertyValue("--acrylic-border")||"rgba(255,255,255,.25)").trim()
      };
    }
    function drawRadar(labels,data){
      const {accent,text,grid}=themeColors();
      if(chart) chart.destroy();
      chart=new Chart(ctx,{
        type:"radar",
        data:{labels,datasets:[{
          data,
          backgroundColor:hex2rgba(accent,.25),
          borderColor:accent,
          borderWidth:2,
          pointBackgroundColor:accent,
          pointRadius:3
        }]},
        options:{
          scales:{r:{
            suggestedMin:0,suggestedMax:40,
            ticks:{stepSize:10,color:text,backdropColor:"transparent"},
            grid:{color:grid},angleLines:{color:grid},
            pointLabels:{color:text,font:{size:12,weight:"500"}}
          }},
          plugins:{legend:{display:false}},
          animation:{duration:500}
        }
      });
    }
    function highlight(codes){
      highlighted.forEach(c=>c.classList.remove("card-highlight"));
      highlighted=[];
      codes.forEach(code=>{
        const sel=`[data-i18n="${PATHS[code]}"]`;
        const card=document.querySelector(sel)?.closest(".career-card");
        if(card){card.classList.add("card-highlight");highlighted.push(card);}
      });
    }
  
    /* =============================================================
       SUBMIT / SCORING
    ============================================================= */
    form.addEventListener("submit",e=>{
      e.preventDefault();
      if(!valid(steps[step])) return;
  
      /* ---------- score collection ----------------------------- */
      const score={F:0,B:0,AI:0,G:0,GM:0};
      form.querySelectorAll("input:checked").forEach(inp=>{
        const w=+inp.dataset.val||1;
        inp.value.split(",").forEach(c=>score[c.trim()]+=w);
      });
      const sorted=Object.entries(score).sort((a,b)=>b[1]-a[1]);
      const [primary,secondary]=sorted;
  
      /* ---------- prepare labels & data ------------------------ */
      const labels=Object.keys(PATHS).map(k=>translations[currentLang][PATHS[k]]);
      const data  =Object.keys(score).map(k=>score[k]);
  
      /* ---------- show box FIRST, then draw chart -------------- */
      resultBox.hidden=false;  // 👈 fix: make canvas visible first
      drawRadar(labels,data);
  
      /* ---------- text outputs --------------------------------- */
      primaryEl.textContent = translations[currentLang][PATHS[primary[0]]];
      secondEl.textContent  = translations[currentLang][PATHS[secondary[0]]];
      const advKey="pdq_advice_"+primary[0];
      document.getElementById("pdq-advice").textContent=
        translations[currentLang][advKey]||"";
  
      /* ---------- highlight cards ------------------------------ */
      highlight([primary[0],secondary[0]]);
      scrollBtn.onclick=()=>highlighted[0]?.scrollIntoView({behavior:"smooth",block:"center"});
  
      /* ---------- scroll to result ----------------------------- */
      resultBox.scrollIntoView({behavior:"smooth"});
    });
  
    /* update chart colors on live theme change (optional) */
    document.addEventListener("themechange",()=>{
      if(!chart) return;
      const {accent,text,grid}=themeColors();
      chart.data.datasets[0].backgroundColor=hex2rgba(accent,.25);
      chart.data.datasets[0].borderColor=accent;
      Object.assign(chart.options.scales.r,{
        grid:{color:grid},angleLines:{color:grid},
        ticks:{color:text},pointLabels:{color:text}
      });
      chart.update();
    });
  
    /* init view */
    showStep(step);
  });

  const { animate, scroll, inView } = Motion;
inView(".learning_path_title", (element) => {
    animate(element, { y: 30},
        { duration: 1 });
    
});

