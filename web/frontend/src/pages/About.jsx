const ACCENTS = {
  eco: {
    bar: 'from-transparent via-eco-400/40 to-transparent',
    title: 'text-eco-400',
    badge: 'text-eco-400 border-eco-400/30 bg-eco-400/10',
  },
  fin: {
    bar: 'from-transparent via-fin-400/40 to-transparent',
    title: 'text-fin-400',
    badge: 'text-fin-400 border-fin-400/30 bg-fin-400/10',
  },
  primary: {
    bar: 'from-transparent via-primary-400/40 to-transparent',
    title: 'text-primary-400',
    badge: 'text-primary-400 border-primary-400/30 bg-primary-400/10',
  },
}

function Section({ title, accent = 'primary', children }) {
  const a = ACCENTS[accent] ?? ACCENTS.primary
  return (
    <section className="bg-navy-900/80 backdrop-blur rounded-lg border border-primary-800/50 overflow-hidden">
      <div className="px-6 py-4 border-b border-primary-800/50 bg-navy-900/50">
        <h2 className={`font-serif text-lg font-semibold ${a.title}`}>{title}</h2>
      </div>
      <div className="px-6 py-5 text-gray-300 font-mono text-sm leading-relaxed space-y-4">
        {children}
      </div>
      <div className={`h-px bg-gradient-to-r ${a.bar}`} />
    </section>
  )
}

function SubHeading({ children }) {
  return (
    <h3 className="font-mono uppercase tracking-wider text-xs text-gray-400 pt-2">
      {children}
    </h3>
  )
}

function VarRow({ name, type, range, desc }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-[minmax(0,270px)_1fr] gap-x-5 gap-y-1 py-2 border-b border-primary-900/30 last:border-b-0">
      <div className="space-y-1 min-w-0">
        {/* Several parameter paths are longer than the column; wrap rather than
            letting them run into the description. */}
        <code className="text-gray-100 break-words">{name}</code>
        {(type || range) && (
          <div className="flex flex-wrap gap-1">
            {type && (
              <span className="inline-block px-1.5 py-0.5 text-[10px] rounded border border-primary-800/50 text-primary-300 bg-navy-800">
                {type}
              </span>
            )}
            {range && (
              <span className="inline-block px-1.5 py-0.5 text-[10px] rounded border border-primary-800/50 text-gray-400 bg-navy-800">
                {range}
              </span>
            )}
          </div>
        )}
      </div>
      <p className="text-gray-400">{desc}</p>
    </div>
  )
}

function Phase({ n, name, children }) {
  return (
    <div className="flex gap-3 py-1.5 border-b border-primary-900/30 last:border-b-0">
      <span className="text-primary-400 tabular-nums shrink-0 w-6 text-right">{n}</span>
      <div>
        <code className="text-gray-100">{name}</code>
        <span className="text-gray-400"> — {children}</span>
      </div>
    </div>
  )
}

function About() {
  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8 animate-slide-up">
      <div>
        <h1 className="font-serif text-3xl font-semibold text-gray-100 tracking-tight">
          About ENVISTRA
        </h1>
        <p className="mt-1 text-sm font-mono uppercase tracking-[0.2em] text-primary-400">
          Description · Configuration Reference · Usage Guide
        </p>
      </div>

      <Section title="Overview & Purpose" accent="eco">
        <p>
          <span className="text-gray-100">ENVISTRA</span> (ENVIronmental STRAtegy) is an
          agent-based model, built on the <span className="text-eco-400">Mesa</span>{' '}
          framework, that simulates how enterprises adapt their behavioural strategies to
          green regulatory constraints: how they split investment between{' '}
          <span className="text-fin-400">financial</span> and{' '}
          <span className="text-eco-400">ecological</span> efficiency, how they adapt
          operating expenses, and how they meet emission-quota obligations inside a
          cap-and-trade market with escalating penalties.
        </p>
        <p>
          Each enterprise is one agent. Every step it forecasts its own costs and
          pollution, receives a quota allocation, trades surplus or shortfall on a shared
          market, produces revenue and emissions, pays any penalty, and reinvests.
          Strategies differ in how much they care about the ecological side and how
          aggressively they trade.
        </p>
        <p>
          The model is <span className="text-gray-100">configuration-driven and
          sector-agnostic</span>. Electricity-generation data for 2010–2019 is used to
          calibrate and validate it, but nothing in the model is specific to that sector.
        </p>
      </Section>

      <Section title="Everything is a Configuration File" accent="primary">
        <p>
          There are no hardcoded strategies and no hardcoded roster. The JSON files under{' '}
          <code className="text-gray-100">config/</code> are the only source of truth, and
          the application refuses to start rather than fall back to stale defaults.
        </p>
        <VarRow
          name="config/environment.json"
          type="one file"
          desc="The regulatory regime: how revenue and pollution are calculated, how quotas are allocated and tightened, and the escalating penalty schedule. Edit it on the Environment page."
        />
        <VarRow
          name="config/strategies/<id>.json"
          type="one per strategy"
          desc="A behavioural strategy: the four estimators and four calculators that decide how an agent forecasts, invests and trades. Any number of strategies is supported — add a file and it is available."
        />
        <VarRow
          name="config/companies/<id>.json"
          type="one per agent"
          desc="One enterprise: which strategy it follows, which historical company supplies its starting position, and its four personal efficiency parameters. The number of files is the number of agents."
        />
        <p className="text-gray-400">
          Configuration is validated when it is read. An unknown key is rejected with a
          spelling suggestion, an approach that is not implemented is refused by name, and
          a strategy that a company still references cannot be deleted.
        </p>
      </Section>

      <Section title="Companies & the Two Flags" accent="fin">
        <p>Each company file carries two independent switches.</p>
        <VarRow
          name="enabled"
          type="boolean"
          range="default true"
          desc="Whether this company takes part in the simulation. A disabled company becomes no agent at all — it neither reports results nor trades quota, so disabling one changes the market for everybody else."
        />
        <VarRow
          name="plot"
          type="boolean"
          range="default true"
          desc="Whether this company appears in the charts. Purely presentational: an enabled company still moves the market whether or not it is drawn."
        />
        <VarRow
          name="color"
          type="hex string"
          range="optional"
          desc="The colour used for this company's line. Omit it and a distinct colour is assigned automatically, stable for a given set of company files."
        />
        <VarRow
          name="dataSource"
          type="string"
          desc="The company name in the source workbooks that supplies this agent's starting assets, expenses, revenue and pollution. Several agents may share one data source — which is how the same company can be run under several strategies side by side."
        />
      </Section>

      <Section title="What Happens in a Step" accent="eco">
        <p>Every agent moves through these phases in order, each step:</p>
        <div>
          <Phase n="1" name="EstimateExpenses">project operating costs for the year</Phase>
          <Phase n="2" name="EstimateInvestments">split investment between financial and ecological efficiency</Phase>
          <Phase n="3" name="EstimatePollution">forecast emissions, by ratio or by a trained neural network</Phase>
          <Phase n="4" name="SendExpensesReport">declare projected costs to the quota manager</Phase>
          <Phase n="5" name="CalculateQuotas">the manager allocates the industry cap</Phase>
          <Phase n="6" name="ReceiveQuota">agents take their allocation</Phase>
          <Phase n="7" name="SellQuota">surplus quota is offered to the market</Phase>
          <Phase n="8" name="SortMarketLotDict">offers are ordered by unit price</Phase>
          <Phase n="9" name="BuyQuota">agents buy what they need, in shuffled order</Phase>
          <Phase n="10" name="ReEstimateExpenses">expenses are adapted to close the remaining gap</Phase>
          <Phase n="11" name="ProduceRevenue">realised revenue, influenced by competitors</Phase>
          <Phase n="12" name="ProducePollution">realised emissions</Phase>
          <Phase n="13" name="PayQuotaExceedancePenalty">tiered penalties on any exceedance</Phase>
          <Phase n="14" name="ImplementInvestments">efficiency improvements take effect</Phase>
          <Phase n="15" name="ImplementOperations">assets and net revenue are updated</Phase>
          <Phase n="16" name="ApplyLinearReductionFactor">the cap tightens for next year</Phase>
        </div>
        <p className="text-gray-400">
          The buy phase runs in shuffled order, so who reaches the market first varies.
          That is one of two sources of randomness — see Reproducibility below.
        </p>
      </Section>

      <Section title="Strategy Parameters" accent="fin">
        <SubHeading>Expenses estimator</SubHeading>
        <VarRow name="approach" type="general | performance_based | performance_based_relative"
          desc="How next year's costs are projected: from assets alone, or adjusted by how the agent performed and whether it exceeded its quota." />
        <VarRow name="changeThreshold_Upper / _Lower" type="number"
          desc="Bounds on how far expenses may move in one step. The lower bound must be below the upper." />
        <VarRow name="featuresImpact" type="{ netRevenue, quotaExceedance }"
          desc="How much each signal drives the adjustment. Weighting quotaExceedance makes an agent react to regulatory pressure rather than profit." />

        <SubHeading>Investment estimator</SubHeading>
        <VarRow name="approach" type="revenue_based | performance_based"
          desc="Whether investment is a fixed share of available revenue, or responds to the recent revenue trend." />
        <VarRow name="investmentRatios" type="{ revenueToInvestmentRatio, minimalInvestment, finInvestment, ecoInvestment }"
          desc="How much is invested, and how it splits between financial and ecological efficiency. The fin/eco split is what most distinguishes one strategy from another." />

        <SubHeading>Pollution estimator</SubHeading>
        <VarRow name="approach" type="general | MLP_based"
          desc="A simple expense-ratio projection, or a small neural network trained on the agent's own history. The forecast drives how much quota it thinks it needs." />
        <VarRow name="mlp" type="optional object"
          desc="Network hyperparameters — layer sizes, solver, iterations, random seed. Omit it to use the documented defaults." />

        <SubHeading>Expenses re-estimation</SubHeading>
        <VarRow name="approach" type="none | gap_proportional"
          desc="After trading, whether the agent cuts expenses to close a remaining emissions gap. `none` means it accepts the penalty instead." />
        <VarRow name="maxReductionRate" type="number" range="0 – 1"
          desc="The most it will cut in one step." />

        <SubHeading>Quota calculators</SubHeading>
        <VarRow name="quota_to_buy/sell_amount.quotaReserve" type="number" range="0 – 1"
          desc="A safety margin held back when deciding how much to trade. A larger reserve means buying more and selling less than strictly needed." />
        <VarRow name="quota_to_buy_price.approach" type="ignorance | economically_efficient | gap_full_cover"
          desc="Ignore the market; buy only while cheaper than the penalty; or cover the whole gap regardless of price." />
        <VarRow name="quota_to_buy_price.assetsPartForTrading" type="number" range="0 – 1"
          desc="The share of free assets the agent is willing to spend on quota." />
        <VarRow name="quota_to_sell_price.approach" type="general | history_based"
          desc="A fixed asking price, or one adjusted by how well previous sales went." />
      </Section>

      <Section title="The Environment" accent="primary">
        <SubHeading>Quota allocation</SubHeading>
        <VarRow name="approach" type="expenses_based | historical_pollution_based | improvement_rewarding | grandfathered_with_tightening"
          desc="How the industry cap is divided: by declared expenses, by historical emissions, with a pool rewarding improvement, or grandfathered with an intensity adjustment." />
        <VarRow name="quota_cap_decreaser" type="number" range="0 – 1"
          desc="Multiplicative annual tightening of the cap." />
        <VarRow name="linear_reduction_factor" type="number" range="0 – 1"
          desc="Per-step linear reduction, in the style of EU ETS Phase 4." />
        <VarRow name="penalty_tiers" type="ascending list"
          desc="Price per unit of exceedance, escalating over time so early non-compliance is survivable and late non-compliance is not. The tiers must ascend and the last must be open-ended." />

        <SubHeading>Revenue & pollution</SubHeading>
        <VarRow name="revenue_calculator.approach" type="industry_based | competitive_industry_based"
          desc="Whether revenue follows the industry distribution alone, or is also pushed by competitors' financial efficiency." />
        <VarRow name="competition_influence" type="number" range="0 – 1"
          desc="How strongly competitors move an agent's revenue." />
        <VarRow name="pollution_calculator.approach" type="industry_based | company_based"
          desc="Whether emissions intensity comes from the industry average or the company's own history." />
      </Section>

      <Section title="Reproducibility" accent="eco">
        <p>
          A run repeats exactly only if you give it a{' '}
          <span className="text-gray-100">seed</span>. There are two independent sources
          of randomness and a seed pins both: the shuffled order of the buy phase, and the
          sampling of realised revenue from its industry distribution.
        </p>
        <p>
          Every run writes <code className="text-gray-100">run_config.json</code> beside
          its charts, recording the seed, the environment regime and every company's fully
          resolved configuration. A <code>null</code> seed there means that run cannot be
          reproduced.
        </p>
        <p className="text-gray-400">
          Results also include <code>model_history.csv</code> — the complete per-agent,
          per-step record for every agent, not only the ones that were charted. Each row
          carries both its <code>Step</code> and its <code>Year</code> (step 1 is the start year).
        </p>
      </Section>

      <Section title="Reading the Charts" accent="primary">
        <p>
          Each run produces a standard set of charts, grouped into basics, pollution,
          quota, quota trading, ratios and efficiency. Only companies marked{' '}
          <code className="text-gray-100">plot</code> appear as lines; the rest still take
          part in the simulation.
        </p>
        <VarRow name="Pollution Difference"
          desc="Realised minus forecast emissions. Close to zero means the agent's pollution estimator is working; large swings mean it is repeatedly mis-sizing its quota needs." />
        <VarRow name="Base Quota Exceedance vs Quota Exceedance"
          desc="Before and after trading. The gap between them is what the market absorbed." />
        <VarRow name="Quota Trade Revenue"
          desc="Income from selling quota minus the cost of buying it. Persistently positive means a strategy is funding itself by staying under its cap." />
        <VarRow name="Financial vs Ecological Efficiency"
          desc="Where each strategy's investment actually went, and what it bought." />
      </Section>

      <Section title="A Note on Comparability" accent="fin">
        <p>
          Results from this version are <span className="text-gray-100">not comparable</span>{' '}
          with the earlier implementation this model was ported from. A defect in the
          quota-buying path destroyed quota instead of returning it to the market when a
          lot turned out to be too expensive; fixing it changes outcomes for every
          strategy that buys economically, and changes the market for all the others.
        </p>
      </Section>
    </div>
  )
}

export default About
