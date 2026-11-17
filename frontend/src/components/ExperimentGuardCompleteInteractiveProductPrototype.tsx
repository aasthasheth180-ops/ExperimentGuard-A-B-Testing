import React, { useState } from 'react';
import { LayoutDashboard, FlaskConical, ChartNoAxesCombined, ShieldCheck, ClipboardCheck, UserRound, Plus, Play, Pause, Settings, LogOut, Trash2 } from 'lucide-react';
const data: {
  experiment_id?: string;
  name: string;
  status: string;
  users: number;
  a: number;
  b: number;
  p: number;
}[] = [{
  name: 'Checkout Redesign',
  status: 'Running',
  users: 12000,
  a: 7.64,
  b: 8.82,
  p: .018
}, {
  name: 'Pricing Page V2',
  status: 'Running',
  users: 8240,
  a: 5.1,
  b: 5.6,
  p: .21
}, {
  name: 'Onboarding Flow',
  status: 'Draft',
  users: 0,
  a: 0,
  b: 0,
  p: 0
}, {
  name: 'Search Layout',
  status: 'Completed',
  users: 18320,
  a: 12.3,
  b: 12.5,
  p: .67
}, {
  name: 'Email CTA',
  status: 'Paused',
  users: 4300,
  a: 4.3,
  b: 4.1,
  p: .55
}];
const nav = [{
  name: 'Overview',
  icon: LayoutDashboard
}, {
  name: 'Experiments',
  icon: FlaskConical
}, {
  name: 'Results',
  icon: ChartNoAxesCombined
}, {
  name: 'Health',
  icon: ShieldCheck
}, {
  name: 'Decisions',
  icon: ClipboardCheck
}];
const box = 'bg-white border border-[#e7eaf1] rounded-xl p-6';
const primary = 'bg-[#5063dc] text-white rounded-lg px-5 py-3 font-semibold hover:bg-[#3c4fc7]';
const input = 'w-full border border-[#e1e6ee] rounded-lg px-3 py-3 mt-2 mb-5';
function Graph() {
  return <div><div className="flex justify-between text-[10px] tracking-widest font-semibold mb-4"><span>CONVERSION PERFORMANCE</span><span className="text-[#98a3b3]">ILLUSTRATIVE</span></div><svg viewBox="0 0 520 190" preserveAspectRatio="none" className="w-full h-52"><g stroke="#e8ebf1" strokeDasharray="4 5">{[40, 90, 140].map(y => <line key={y} x1="0" x2="520" y1={y} y2={y} />)}</g><path className="eg-line" stroke="#aeb8c7" strokeWidth="3" fill="none" d="M0 160 C100 145 160 132 250 120 S420 100 520 80" /><path className="eg-line" stroke="#5063dc" strokeWidth="3" fill="none" d="M0 160 C100 139 160 112 250 92 S420 42 520 18" /><circle r="5" fill="#5063dc"><animateMotion dur="9s" repeatCount="indefinite" path="M0 160 C100 139 160 112 250 92 S420 42 520 18" /></circle></svg><div className="flex gap-5 text-xs text-[#8995a7] mt-2"><span>● Control A</span><span className="text-[#5063dc]">● Variant B</span></div></div>;
}
function LoginScreen({
  onSuccess
}: {
  onSuccess: () => void;
}) {
  const [typed, setTyped] = React.useState('');
  React.useEffect(() => {
    let index = 0;
    const label = 'ExperimentGuard';
    const timer = window.setInterval(() => {
      index += 1;
      setTyped(label.slice(0, index));
      if (index >= label.length) window.clearInterval(timer);
    }, 115);
    return () => window.clearInterval(timer);
  }, []);
  const [mode, setMode] = React.useState<'Sign in' | 'Create account'>('Sign in');
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [fullName, setFullName] = React.useState('');
  const [visible, setVisible] = React.useState(false);
  const [remember, setRemember] = React.useState(true);
  const [error, setError] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [forgot, setForgot] = React.useState(false);
  const [notice, setNotice] = React.useState('');
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setNotice('');

    if (!/^\S+@\S+\.\S+$/.test(email)) {
        setError('Enter a valid email address.');
        return;
    }

    if (forgot) {
        setNotice('Password reset is not available yet.');
        return;
    }

    if (mode === 'Create account') {
        if (fullName.trim().length < 2) {
        setError('Please enter your full name.');
        return;
        }
    }

    if (password.length < 8) {
        setError('Password must contain at least 8 characters.');
        return;
    }

    setLoading(true);

    try {
        const endpoint =
        mode === 'Sign in'
            ? '/auth/login'
            : '/auth/register';

      const response = await fetch(
          `http://127.0.0.1:8000${endpoint}`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(
              mode === 'Sign in'
                ? { email, password }
                : {
                    email,
                    password,
                    full_name: fullName.trim(),
                  }
            ),
          }
        );

        const result = await response.json();

        if (!response.ok) {
        throw new Error(
            typeof result.detail === 'string'
            ? result.detail
            : 'Authentication failed.'
        );
        }

        if (mode === 'Create account') {
        setNotice('Account created! Please sign in.');
        setMode('Sign in');
        setPassword('');
        return;
        }

        if (!result.access_token) {
        throw new Error('Login response did not contain an access token.');
        }

        // Temporary session storage for local development.
        sessionStorage.setItem(
        'experimentguard_token',
        result.access_token
        );

        onSuccess();
    } catch (err) {
        setError(
        err instanceof Error
            ? err.message
            : 'Unable to connect to the server.'
        );
    } finally {
        setLoading(false);
    }
    };


  return <div className="max-w-6xl mx-auto px-6 md:px-12 py-7">
  <div className="flex gap-3 items-center"><span className="bg-[#1d2940] text-white rounded-xl p-3 font-serif">EG</span><div><div className="font-serif text-2xl md:text-3xl font-semibold">ExperimentGuard<span className="text-[#5063dc]">.</span></div><div className="text-[9px] tracking-[.18em] text-[#8a95a6]">EXPERIMENT INTELLIGENCE PLATFORM</div></div></div>
  <div className="grid lg:grid-cols-2 gap-10 lg:gap-20 items-center min-h-[680px] py-10">
   <section className="eg-enter"><div className="text-[#5063dc] text-xs tracking-[.2em] font-bold">THE EXPERIMENT LAB</div><h1 className="font-serif text-5xl md:text-6xl my-6 leading-[1.12]">Every experiment<br /><em className="text-[#5063dc]">tells a story.</em></h1><p className="text-[#758296] leading-7 mb-8">Measure impact. Understand uncertainty.<br />Make better rollout decisions.</p>
    <div className="bg-white border border-[#e7eaf1] rounded-2xl p-5 md:p-7 shadow-[0_20px_70px_-35px_rgba(30,43,67,.25)]"><div className="flex justify-between items-center text-xs font-bold"><span>EXPERIMENT PREVIEW</span><span className="text-[#258469] bg-[#eaf8f1] rounded-full px-3 py-1 text-[10px]">● SIMULATION</span></div><div className="flex justify-between text-[11px] text-[#8895a7] my-6"><span>01 / Assign</span><span>02 / Measure</span><span>03 / Decide</span></div><Graph /><div className="flex gap-4 mt-6 pt-5 border-t border-[#edf0f5] text-xs text-[#718095]"><span><b className="text-[#1e2b43]">A/B</b> comparison</span><span>•</span><span>Evidence-led decisions</span></div></div>
   </section>
   <section className="eg-enter bg-white border border-[#e7eaf1] rounded-2xl p-7 md:p-10 shadow-[0_24px_80px_-40px_rgba(30,43,67,.3)]" aria-label="Account access">
    <div className="text-[#5063dc] tracking-[.2em] text-[10px] font-bold">YOUR WORKSPACE</div><h2 className="font-serif text-4xl mt-4">{forgot ? 'Reset your password.' : mode === 'Sign in' ? <><span>Welcome to </span><span className="text-[#5063dc]">{typed}</span>{typed.length < 'ExperimentGuard'.length && <span className="eg-cursor" aria-hidden="true" />}</> : 'Create your workspace.'}</h2><p className="text-[#7f8b9d] mt-3 text-sm leading-6">{forgot ? 'Enter your email to preview the recovery flow.' : 'Your home for experiments, insights, and confident decisions.'}</p>
    {!forgot && <div className="flex gap-8 border-b mt-8 mb-6" role="tablist" aria-label="Authentication mode">{(['Sign in', 'Create account'] as const).map(t => <button type="button" role="tab" aria-selected={mode === t} key={t} onClick={() => {
            setMode(t);
            setError('');
            setNotice('');
          }} className={'pb-3 text-sm transition-colors ' + (mode === t ? 'border-b-2 border-[#5063dc] text-[#5063dc] font-semibold' : 'text-[#8995a6] hover:text-[#1e2b43]')}>{t}</button>)}</div>}
    <form onSubmit={submit} className={forgot ? 'mt-8' : ''} noValidate>
     {!forgot && mode === 'Create account' && <label className="block text-sm font-semibold mb-4">Full name<input autoComplete="name" value={fullName} onChange={e => setFullName(e.target.value)} placeholder="Your full name" className="eg-auth-input" /></label>}
     <label className="block text-sm font-semibold mb-4">Email address<input type="email" autoComplete="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="your@email.com" className="eg-auth-input" /></label>
     {!forgot && <label className="block text-sm font-semibold mb-3">Password<div className="relative"><input type={visible ? 'text' : 'password'} autoComplete={mode === 'Sign in' ? 'current-password' : 'new-password'} value={password} onChange={e => setPassword(e.target.value)} placeholder="At least 8 characters" className="eg-auth-input !pr-20" /><button type="button" onClick={() => setVisible(!visible)} className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-medium text-[#5063dc]" aria-label={visible ? 'Hide password' : 'Show password'}>{visible ? 'Hide' : 'Show'}</button></div></label>}
     {!forgot && mode === 'Sign in' && <div className="flex justify-between items-center mb-6 text-xs"><label className="flex items-center gap-2 text-[#718095]"><input type="checkbox" checked={remember} onChange={e => setRemember(e.target.checked)} className="accent-[#5063dc]" /> Remember me</label><button type="button" onClick={() => {
              setForgot(true);
              setError('');
              setNotice('');
            }} className="text-[#5063dc] font-semibold hover:underline">Forgot password?</button></div>}
     {error && <p role="alert" className="mb-4 text-sm text-[#ad3d4a] bg-[#fff1f2] p-3 rounded-lg">{error}</p>}
     {notice && <p role="status" className="mb-4 text-sm text-[#24795e] bg-[#eaf8f1] p-3 rounded-lg">{notice}</p>}
     <button disabled={loading} type="submit" className="w-full bg-[#5063dc] text-white rounded-xl px-5 py-3.5 font-semibold hover:bg-[#3c4fc7] transition-all hover:-translate-y-0.5 disabled:opacity-60 disabled:translate-y-0 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#5063dc]">{loading ? 'Please wait…' : forgot ? 'Preview password reset' : mode === 'Sign in' ? 'Sign in to workspace ' : 'Create a account'}</button>
     {forgot && <button type="button" onClick={() => {
            setForgot(false);
            setNotice('');
          }} className="w-full mt-4 text-sm text-[#5063dc] font-semibold">Back to sign in</button>}
    </form>
    <p className="text-center text-xs text-[#9aa4b4] mt-6">Interactive prototype · No real authentication or emails</p>
   </section>
  </div>
 </div>;
}
type BackendExperiment = {
  experiment_id: string;
  name: string;
  variants: Record<string, number>;
  primary_metric: string;
  status: string;
};
export const ExperimentGuardCompleteInteractiveProductPrototype = () => {
  const [page, P] = useState(() =>
  sessionStorage.getItem('experimentguard_token')
    ? 'Overview'
    : 'Login / Register'
),

    [rows, R] = useState<typeof data>([]),
    [selected, S] = useState(0),
    [detail, D] = useState('Results'),
    [menu, M] = useState(false),
    [name, N] = useState(''),
    [search, Q] = useState(''),
    [status, F] = useState('All'),
    [modal, B] = useState('');

  const [primaryMetric, setPrimaryMetric] = useState('conversion_rate');
  const [plannedSampleSize, setPlannedSampleSize] = useState('12000');
  const [hypothesis, setHypothesis] = useState('');
  const [experimentMetrics, setExperimentMetrics] = useState<{
  experiment_id: string;
  variants: Record<string, {
    assigned_users: number;
    converted_users: number;
    conversion_rate: number;
  }>;
  relative_lift_percent: number | null;
} | null>(null);
  const [sessionVersion, setSessionVersion] = useState(0);
  const [accountEmail, setAccountEmail] = useState('');
  const [experimentStatistics, setExperimentStatistics] = useState<{
  experiment_id: string;
  statistics: {
    p_value: number;
    z_statistic: number | null;
    is_significant: boolean;
    normal_approximation_valid: boolean;
    confidence_interval: {
      lower: number;
      upper: number;
    };
  };
} | null>(null);

  const [experimentHealth, setExperimentHealth] = useState<{
    experiment_id: string;
    status: string;
    validation: {
      is_valid: boolean;
      total_users: number;
      missing_variants: string[];
      unexpected_variants: string[];
      negative_count_variants: string[];
      issues: string[];
    };
    srm: {
      total_users: number;
      observed_counts: Record<string, number>;
      expected_weights: Record<string, number>;
      observed_ratios: Record<string, number>;
      chi_square: number;
      p_value: number;
      alpha: number;
      has_srm: boolean;
    };
  } | null>(null);

  const [healthSummary, setHealthSummary] = useState({
      checked: 0,
      healthy: 0,
      warnings: 0,
      unassessed: 0,
    });

  const [resultsExperimentId, setResultsExperimentId] = useState('');
  const [resultsMetrics, setResultsMetrics] = useState<{
  experiment_id: string;
  variants: Record<string, {
    assigned_users: number;
    converted_users: number;
    conversion_rate: number;
  }>;
  relative_lift_percent: number | null;
} | null>(null);

const [resultsStatistics, setResultsStatistics] = useState<{
  experiment_id: string;
  statistics: {
    p_value: number;
    z_statistic: number | null;
    is_significant: boolean;
    normal_approximation_valid: boolean;
    confidence_interval: {
      lower: number;
      upper: number;
    };
  };
} | null>(null);

  const [decisionSummaries, setDecisionSummaries] = useState<
    Record<
      string,
      {
        decision: string;
        health_status: string;
        reason: string;
      }
    >
  >({});

  const [experimentDecision, setExperimentDecision] = useState<{
    experiment_id: string;
    decision: string;
    health_status: string;
    reason: string;
  } | null>(null);

  const [experimentDetails, setExperimentDetails] = useState<{
    experiment_id: string;
    name: string;
    hypothesis: string | null;
    variants: Record<string, number>;
    primary_metric: string;
    planned_sample_size: number | null;
    status: string;
} | null>(null);
  React.useEffect(() => {
    const loadExperiments = async () => {
      const token = sessionStorage.getItem('experimentguard_token');

      if (!token) return;

      try {
        const response = await fetch(
          'http://127.0.0.1:8000/experiments',
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error(`Failed to load experiments: ${response.status}`);
        }

        const experiments: BackendExperiment[] = await response.json();

        R(
          experiments.map((experiment) => ({
            experiment_id: experiment.experiment_id!,
            name: experiment.name,
            status:
              experiment.status.charAt(0).toUpperCase() +
              experiment.status.slice(1).toLowerCase(),
            users: 0,
            a: 0,
            b: 0,
            p: 0,
          }))
        );


    const healthResults = await Promise.allSettled(
      experiments.map(async (experiment) => {
        const healthResponse = await fetch(
              `http://127.0.0.1:8000/experiments/${encodeURIComponent(experiment.experiment_id!)}/health`,
              {
                headers: {
                  Authorization: `Bearer ${token}`,
                },
              }
            );

        if (!healthResponse.ok) {
              throw new Error(`Health check failed: ${healthResponse.status}`);
            }

        return healthResponse.json() as Promise<{
              status: string;
            }>;
          })
        );

      const checked = healthResults.filter(
          (result) => result.status === 'fulfilled'
        ).length;

      const healthy = healthResults.filter(
        (result) =>
          result.status === 'fulfilled' &&
          result.value.status === 'healthy'
      ).length;

      setHealthSummary({
        checked,
        healthy,
        warnings: checked - healthy,
        unassessed: experiments.length - checked,
      });

      } catch (error) {
        console.error('Could not load experiments:', error);
      }
      };

      loadExperiments();
      }, [sessionVersion]);



  React.useEffect(() => {
    if (page !== 'Decisions') return;

    const token = sessionStorage.getItem('experimentguard_token');
    if (!token) return;

    let cancelled = false;

    const loadDecisions = async () => {
      const results = await Promise.allSettled(
        rows
          .filter((experiment) => Boolean(experiment.experiment_id))
          .map(async (experiment) => {
            const response = await fetch(
              `http://127.0.0.1:8000/experiments/${encodeURIComponent(
                experiment.experiment_id!
              )}/decision`,
              {
                headers: {
                  Authorization: `Bearer ${token}`,
                },
              }
            );

            if (!response.ok) {
              throw new Error(`Decision API returned ${response.status}`);
            }

            const data = await response.json();

            return {
              experimentId: experiment.experiment_id!,
              decision: data.decision as string,
              health_status: data.health_status as string,
              reason: data.reason as string,
            };
          })
      );

      if (cancelled) return;

      const summaries: Record<
        string,
        {
          decision: string;
          health_status: string;
          reason: string;
        }
      > = {};

      for (const result of results) {
        if (result.status === 'fulfilled') {
          summaries[result.value.experimentId] = {
            decision: result.value.decision,
            health_status: result.value.health_status,
            reason: result.value.reason,
          };
        }
      }

      setDecisionSummaries(summaries);
    };

    loadDecisions().catch((error) => {
      if (!cancelled) {
        console.error('Could not load decisions:', error);
      }
    });

    return () => {
      cancelled = true;
    };
  }, [page, rows, sessionVersion]);




    React.useEffect(() => {
      if (!resultsExperimentId) {
        setResultsMetrics(null);
        setResultsStatistics(null);
        return;
      }

      let cancelled = false;

      const loadResults = async () => {
        const token = sessionStorage.getItem('experimentguard_token');

        if (!token) return;

        setResultsMetrics(null);
        setResultsStatistics(null);

        const experimentId = encodeURIComponent(resultsExperimentId);

        try {
          const [metricsResponse, statisticsResponse] = await Promise.all([
            fetch(`http://127.0.0.1:8000/experiments/${experimentId}/metrics`, {
              headers: { Authorization: `Bearer ${token}` },
            }),
            fetch(`http://127.0.0.1:8000/experiments/${experimentId}/statistics`, {
              headers: { Authorization: `Bearer ${token}` },
            }),
          ]);

          const metricsData = metricsResponse.ok
            ? await metricsResponse.json()
            : null;

          const statisticsData = statisticsResponse.ok
            ? await statisticsResponse.json()
            : null;

          if (!cancelled) {
            setResultsMetrics(metricsData);
            setResultsStatistics(statisticsData);
          }
        } catch (error) {
          if (!cancelled) {
            console.error('Could not load results:', error);
            setResultsMetrics(null);
            setResultsStatistics(null);
          }
        }
      };

      loadResults();

      return () => {
        cancelled = true;
      };
      }, [resultsExperimentId, sessionVersion]);


    React.useEffect(() => {
    if (!resultsExperimentId) {
      setResultsMetrics(null);
      setResultsStatistics(null);
      return;
    }

    let cancelled = false;

    const loadResults = async () => {
      const token = sessionStorage.getItem('experimentguard_token');

      if (!token) return;

      setResultsMetrics(null);
      setResultsStatistics(null);

      const experimentId = encodeURIComponent(resultsExperimentId);

      try {
        const [metricsResponse, statisticsResponse] = await Promise.all([
          fetch(`http://127.0.0.1:8000/experiments/${experimentId}/metrics`, {
            headers: { Authorization: `Bearer ${token}` },
          }),
          fetch(`http://127.0.0.1:8000/experiments/${experimentId}/statistics`, {
            headers: { Authorization: `Bearer ${token}` },
          }),
        ]);

        if (!cancelled) {
          if (metricsResponse.ok) {
            setResultsMetrics(await metricsResponse.json());
          }

          if (statisticsResponse.ok) {
            setResultsStatistics(await statisticsResponse.json());
          }
        }
      } catch (error) {
        if (!cancelled) {
          console.error('Could not load results:', error);
        }
      }
    };

    loadResults();

    return () => {
      cancelled = true;
    };
  }, [resultsExperimentId, sessionVersion]);

const createExperiment = async () => {
  const experimentName = name.trim();
  const sampleSize = Number(plannedSampleSize);

  if (
    plannedSampleSize.trim() === '' ||
    !Number.isSafeInteger(sampleSize) ||
    sampleSize <= 0
  ) {
    alert('Please enter a valid positive sample size.');
    return;
  }

  if (!experimentName) {
    alert('Please enter an experiment name.');
    return;
  }
    const token = sessionStorage.getItem('experimentguard_token');

    if (!token) {
      alert('Please sign in again.');
      go('Login / Register');
      return;
    }

    const experimentId =
      'exp_' + crypto.randomUUID().replace(/-/g, '');

    try {
      const response = await fetch(
        'http://127.0.0.1:8000/experiments',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
          experiment_id: experimentId,
          name: experimentName,
          hypothesis: hypothesis.trim() || null,
          variants: { A: 0.5, B: 0.5 },
          primary_metric: primaryMetric,
          planned_sample_size: sampleSize,
        }),
        }
        );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof result.detail === 'string'
            ? result.detail
            : `Could not create experiment (${response.status})`
        );
      }

      const newExperiment = {
        experiment_id: result.experiment_id ?? experimentId,
        name: result.name ?? experimentName,
        status: 'Draft',
        users: 0,
        a: 0,
        b: 0,
        p: 0,
      };

      R(previous => [newExperiment, ...previous]);
      S(0);
      N('');
      setHypothesis('');
      go('Experiment Details');

    } catch (error) {
      alert(
        error instanceof Error
          ? error.message
          : 'Failed to create experiment.'
      );
    }
  };

React.useEffect(() => {
  const validateSession = async () => {
    const token = sessionStorage.getItem('experimentguard_token');

    if (!token) {
      P('Login / Register');
      return;
    }

    try {
      const response = await fetch('http://127.0.0.1:8000/auth/me', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
          sessionStorage.removeItem('experimentguard_token');
          setAccountEmail('');
          P('Login / Register');
          return;
}

      const user = await response.json();
      setAccountEmail(user.email ?? '');
    } catch (error) {
      console.error('Could not validate session:', error);
    }
  };

  validateSession();
}, [sessionVersion]);

  const cur = rows[selected] || rows[0] || {
  name: 'No experiment selected',
  status: 'Draft',
  users: 0,
  a: 0,
  b: 0,
  p: 0,
};
  const go = (s: string) => {
    P(s);
    M(false);
  };

  const change = async (newStatus: string) => {
    const experiment = rows[selected];

    if (!experiment?.experiment_id) {
      alert('Experiment ID not found.');
      return;
    }

    const token = sessionStorage.getItem('experimentguard_token');

    if (!token) {
      alert('Please sign in again.');
      return;
    }

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/experiments/${encodeURIComponent(experiment.experiment_id)}/status`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            status: newStatus.toLowerCase(),
          }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update experiment status');
      }

      const result = await response.json();

      R(previous =>
        previous.map((item, index) =>
          index === selected
            ? {
                ...item,
                status: result.status.charAt(0).toUpperCase() +
                  result.status.slice(1).toLowerCase(),
              }
            : item
        )
      );

      setExperimentDetails(previous =>
        previous ? { ...previous, status: result.status } : previous
      );

    } catch (error) {
      console.error('Status update failed:', error);
      alert(error instanceof Error ? error.message : 'Status update failed.');
    }
  };

    const open = async (i: number) => {
      S(i);
      D('Setup');
      setExperimentDetails(null);
      setExperimentMetrics(null);
      setExperimentStatistics(null);
      setExperimentHealth(null);
      setExperimentDecision(null);
      go('Experiment Details');
    const experiment = rows[i];

    if (!experiment?.experiment_id) {
      alert('Experiment ID not found.');
      return;
    }

  const token = sessionStorage.getItem('experimentguard_token');

  if (!token) {
    alert('Please sign in again.');
    return;
  }

  S(i);
  D('Setup');
  setExperimentDetails(null);
  go('Experiment Details');

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/experiments/${encodeURIComponent(experiment.experiment_id)}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to load experiment: ${response.status}`);
    }

    const result = await response.json();
    setExperimentDetails(result);
    const metricsResponse = await fetch(
      `http://127.0.0.1:8000/experiments/${encodeURIComponent(experiment.experiment_id)}/metrics`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!metricsResponse.ok) {
      throw new Error(`Failed to load metrics: ${metricsResponse.status}`);
    }

    const metricsResult = await metricsResponse.json();
    setExperimentMetrics(metricsResult);

    const statisticsResponse = await fetch(
      `http://127.0.0.1:8000/experiments/${encodeURIComponent(experiment.experiment_id)}/statistics`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (statisticsResponse.ok) {
      const statisticsResult = await statisticsResponse.json();
      setExperimentStatistics(statisticsResult);
    } else {
      setExperimentStatistics(null);
    }

    const healthResponse = await fetch(
          `http://127.0.0.1:8000/experiments/${encodeURIComponent(experiment.experiment_id)}/health`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

    if (healthResponse.ok) {
      const healthResult = await healthResponse.json();
      setExperimentHealth(healthResult);
    } else {
          setExperimentHealth(null);
        }

    const decisionResponse = await fetch(
        `http://127.0.0.1:8000/experiments/${encodeURIComponent(experiment.experiment_id)}/decision`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

    if (decisionResponse.ok) {
        const decisionResult = await decisionResponse.json();
        setExperimentDecision(decisionResult);
    } else {
        setExperimentDecision(null);
      }

  } catch (error) {
    console.error('Could not load experiment details:', error);
    alert('Unable to load experiment details.');
  }
};
  const heading = (eyebrow: string, title: string, sub: string) => <div className="mb-8"><div className="text-[#5063dc] text-[10px] font-bold tracking-[.2em]">{eyebrow}</div><h1 className="font-serif text-4xl md:text-5xl my-3">{title}<span className="text-[#5063dc]">.</span></h1><p className="text-[#8b96a6]">{sub}</p></div>;
  const metric = (label: string, value: string) => <div className={box}><div className="text-[10px] text-[#8e99aa] font-bold tracking-widest">{label}</div><div className="font-serif text-4xl mt-4">{value}</div><p className="text-[#a2aab7] text-xs mt-2"></p><p>Live experiment data</p></div>;
  const table = (arr: typeof data) => <div className="overflow-x-auto"><table className="w-full text-sm text-left"><thead><tr className="border-b text-[#9aa4b4] text-[10px] tracking-widest">{['EXPERIMENT', 'STATUS', 'USERS', 'A', 'B'].map(s => <th className="py-4" key={s}>{s}</th>)}</tr></thead><tbody>{arr.map(e => <tr key={e.name} className="border-b border-[#edf0f5] cursor-pointer hover:bg-[#f8f9ff]" onClick={() => open(rows.indexOf(e))}><td className="py-5 font-semibold">{e.name}</td><td><span className="bg-[#eef0ff] text-[#5063dc] rounded-full px-3 py-1 text-xs">{e.status}</span></td><td>{e.users.toLocaleString()}</td><td>{e.users ? e.a + '%' : '—'}</td><td>{e.users ? e.b + '%' : '—'}</td></tr>)}</tbody></table></div>;
  return <div className="min-h-screen bg-[#fafbfe] text-[#1e2b43] font-sans"><style>{`
  @keyframes egtype {
    0% { width: 0; }
    30%, 75% { width: 15ch; } /* Holds full text */
    90%, 100% { width: 0; }   /* Deletes and rests at 0 */
  }

  @keyframes egblink {
    0%, 100% { border-right-color: #5063dc; }
    50% { border-right-color: transparent; }
  }

  @keyframes egdraw {
    0% { stroke-dashoffset: 700; opacity: 0; }
    20% { opacity: 1; }
    60%, 80% { stroke-dashoffset: 0; opacity: 1; }
    100% { stroke-dashoffset: 700; opacity: 0; }
  }

  .eg-type {
    display: inline-block;
    white-space: nowrap;
    overflow: hidden;
    width: 0;
    border-right: 2px solid #5063dc;
    animation:
      egtype 8s ease-in-out infinite,
      egblink 0.7s step-end infinite;
  }

  .eg-line {
    stroke-dasharray: 700;
    stroke-dashoffset: 700;
    animation: egdraw 8s ease-in-out infinite;
  }

  @media (prefers-reduced-motion: reduce) {
    .eg-type {
      animation: none;
      width: auto;
      border-right: none;
    }

    .eg-line {
      animation: none;
      stroke-dashoffset: 0;
    }
  }
`}</style>{page === 'Login / Register' ? <LoginScreen onSuccess={() => {setSessionVersion(v => v + 1); go('Overview')}} /> : <div className="flex min-h-screen"><aside className="w-[72px] bg-white border-r border-[#e9edf3] flex flex-col items-center gap-7 py-6 sticky top-0 h-screen shrink-0"><button className="bg-[#1d2940] text-white font-serif w-10 h-10 rounded-xl" onClick={() => go('Overview')}>EG</button><div className="flex flex-col gap-4">{nav.map(n => <button title={n.name} key={n.name} onClick={() => go(n.name)} className={'w-10 h-10 grid place-items-center rounded-lg ' + (page === n.name ? 'bg-[#edf0ff] text-[#5063dc]' : 'text-[#9ba6b5] hover:bg-[#f5f6fb]')}><n.icon size={20} /></button>)}</div><button className="mt-auto text-[#8c98a9]" onClick={() => M(!menu)}><UserRound size={22} /></button>{menu && <div className="absolute bottom-4 left-16 w-60 bg-white rounded-xl border shadow-xl p-4 z-20"><b>My Account</b><p className="text-xs text-[#8b96a6] my-3">demo@experimentguard.io</p><button className="flex gap-2 py-2" onClick={() => go('Account Settings')}><Settings size={16} /> Settings</button><button className="flex gap-2 py-2" onClick={() => go('Login / Register')}><LogOut size={16} /> Log out</button><button className="flex gap-2 py-2 text-red-600" onClick={() => {
            go('Account Settings');
            B('delete');
          }}><Trash2 size={16} /> Delete account</button></div>}</aside><main className="flex-1 min-w-0"><div className="h-16 bg-white border-b border-[#edf0f5] flex items-center justify-between px-6 md:px-10 text-[10px] tracking-widest text-[#9aa5b4]">WORKSPACE / {page.toUpperCase()} </div><div className="max-w-7xl mx-auto p-6 md:p-10">{page === 'Overview' && <><div className="flex flex-col sm:flex-row sm:justify-between sm:items-end gap-5 mb-8"><div><div className="text-[#5063dc] text-[10px] font-bold tracking-[.2em]">WORKSPACE / OVERVIEW</div><h1 className="font-serif text-4xl md:text-5xl mt-3">Your experiment lab<span className="text-[#5063dc]">.</span></h1><p className="text-[#8793a5] mt-3">A clearer view of every hypothesis, result, and next decision.</p></div><button className={primary + " self-start sm:self-auto shadow-md shadow-indigo-100"} onClick={() => go('Create Experiment')}><Plus size={16} className="inline mr-2" />New experiment</button></div>
<div className="bg-[#eef0ff] border border-[#dfe4ff] rounded-2xl px-5 py-4 mb-6 flex flex-col sm:flex-row sm:justify-between gap-3"><div><div className="text-[#5063dc] text-[10px] font-bold tracking-widest">EXPERIMENT INTELLIGENCE</div><p className="text-sm mt-2 text-[#35435b]"><b>Welcome to your workspace.</b> Track performance and investigate experiment health before making a rollout decision.</p></div><span className="text-[10px] font-semibold tracking-wider text-[#5063dc] whitespace-nowrap">● DEMO DATA</span></div>
<div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">{metric('TOTAL EXPERIMENTS', String(rows.length))}{metric('RUNNING NOW', String(rows.filter(e => e.status === 'Running').length))}{metric('PARTICIPANTS', rows.reduce((n, e) => n + e.users, 0).toLocaleString())}{metric('COMPLETED', String(rows.filter(e => e.status === 'Completed').length))}</div>
<div className="grid lg:grid-cols-[1.7fr_1fr] gap-5 mb-5"><section className={box + " eg-dashboard-card"}><div className="flex justify-between gap-3 items-start mb-5"><div><h3 className="font-serif text-2xl">Conversion performance</h3><p className="text-xs text-[#9aa4b4] mt-2">Control versus variant · illustrative trend</p></div><span className="bg-[#eef0ff] text-[#5063dc] text-[10px] rounded-full px-3 py-1">Preview</span></div><Graph /></section><section className={box + " eg-dashboard-card"}><h3 className="font-serif text-2xl">Experiment status</h3><p className="text-xs text-[#9aa4b4] mt-2 mb-8">Current lifecycle distribution</p>{['Running', 'Draft', 'Paused', 'Completed'].map((status, i) => <div className="mb-6" key={status}><div className="flex justify-between text-sm mb-2"><span className="text-[#5d6b80]">{status}</span><b>{rows.filter(e => e.status === status).length}</b></div><div className="h-2.5 rounded-full bg-[#eff1f6] overflow-hidden"><div className="h-full rounded-full eg-progress" style={{
                      width: (rows.length ? rows.filter(e => e.status === status).length / rows.length * 100 : 0) + '%',
                      background: ['#5063dc', '#adb8c7', '#e5ad60', '#58a68b'][i]
                    }} /></div></div>)}</section></div>
<div className="grid lg:grid-cols-[1.7fr_1fr] gap-5"><section className={box + " eg-dashboard-card"}><div className="flex items-center justify-between mb-5 gap-3"><div><h3 className="font-serif text-2xl">Recent experiments</h3><p className="text-xs text-[#9aa4b4] mt-2">Select an experiment to inspect details</p></div><button className="text-[#5063dc] text-sm font-semibold hover:underline" onClick={() => go('Experiments')}>View all ↗</button></div>{table(rows.slice(0, 4))}</section><section className={box + " eg-dashboard-card"}><h3 className="font-serif text-2xl mb-2">Needs attention</h3><p className="text-xs text-[#9aa4b4] mb-6">Review signals before deciding</p><div className="rounded-xl bg-[#fff8ed] border border-[#f5e7cb] p-4 mb-3"><div className="font-semibold text-sm">Experiment diagnostics</div><p className="text-xs text-[#7d8797] mt-2 leading-5">Check sample ratio mismatch and event quality for running tests.</p><button className="text-[#5063dc] text-xs font-semibold mt-3 hover:underline" onClick={() => go('Health')}>Open health monitor ↗</button></div><div className="rounded-xl bg-[#f5f6ff] border border-[#e8eaff] p-4"><div className="font-semibold text-sm">Review your results</div><p className="text-xs text-[#7d8797] mt-2 leading-5">Interpret effect size and uncertainty before rollout.</p><button className="text-[#5063dc] text-xs font-semibold mt-3 hover:underline" onClick={() => go('Results')}>Explore results ↗</button></div></section></div></>}{page === 'Experiments' && <>{heading('WORKSPACE / EXPERIMENTS', 'Experiments', 'Manage the lifecycle of controlled tests.')}<button className={primary + ' mb-5'} onClick={() => go('Create Experiment')}>+ New experiment</button><div className={box}><div className="flex gap-3 mb-5"><input className={input + ' !m-0'} placeholder="Search experiments" value={search} onChange={e => Q(e.target.value)} /><select className={input + ' !m-0 max-w-36'} value={status} onChange={e => F(e.target.value)}>{['All', 'Running', 'Draft', 'Paused', 'Completed'].map(s => <option key={s}>{s}</option>)}</select></div>{table(rows.filter(e => e.name.toLowerCase().includes(search.toLowerCase()) && (status === 'All' || status === e.status)))}</div></>}{page === 'Create Experiment' && <>{heading('EXPERIMENTS / CREATE', 'New experiment', 'Define the hypothesis, allocation, and measurement plan.')}<div className="grid lg:grid-cols-2 gap-5"><div className={box}><h3 className="font-semibold text-lg mb-5">01 / Experiment setup</h3><label>Name<input className={input} value={name} onChange={e => N(e.target.value)} placeholder="Homepage CTA test" /></label><label>Hypothesis<textarea className={input} rows={3} placeholder="We believe..." value={hypothesis} onChange={(e) =>setHypothesis(e.target.value)} maxLength={5000} /></label><label>Primary metric<select className={input} value={primaryMetric}  onChange={(e) => setPrimaryMetric(e.target.value)}><option value ="conversion_rate">Conversion rate</option><option value ="signup_rate">Signup rate</option></select></label><h3 className="font-semibold text-lg my-5">02 / Traffic allocation</h3><div className="flex h-3 rounded overflow-hidden"><span className="w-1/2 bg-[#adb8c7]" /><span className="w-1/2 bg-[#5063dc]" /></div><p className="text-xs text-[#8c98a9] my-3">50% Control A / 50% Variant B</p><label>Planned sample size<input className={input} type="number" min={1}
    value={plannedSampleSize}
    onChange={(e) => setPlannedSampleSize(e.target.value)}/></label><button
          type="button"
          className={primary + ' w-full'}
          onClick={createExperiment}

              >Create draft</button></div><div className={box}><h3 className="font-semibold text-lg mb-5">Design checklist</h3>{['Define measurable hypothesis', 'Choose primary metric', 'Set stable allocation', 'Plan sample size', 'Monitor SRM and event quality'].map((s, i) => <p key={s} className="py-5 border-b border-[#edf0f5]"><span className="text-[#5063dc] mr-4">0{i + 1}</span>{s}</p>)}<p className="text-xs text-[#8d98a8] mt-5">A planned sample size is not a power calculation.</p></div></div></>}{page === 'Experiment Details' && <>{heading('EXPERIMENT / DETAILS', experimentDetails?.name ?? cur.name, 'Inspect setup, diagnostics, results and summary.')}<div className="flex gap-3 mb-6 flex-wrap"><span className="bg-[#eef0ff] text-[#5063dc] rounded-full px-4 py-3">{cur.status}</span>{cur.status === 'Draft' && <button className={primary} onClick={() => change('Running')}><Play size={15} className="inline" /> Start</button>}{cur.status === 'Running' && <button className={primary} onClick={() => change('Paused')}><Pause size={15} className="inline" /> Pause</button>}{cur.status === 'Paused' && <button className={primary} onClick={() => change('Running')}>Resume</button>}{['Running', 'Paused'].includes(cur.status) && <button className="border rounded-lg px-4" onClick={() => B('complete')}>Complete</button>}</div><div className="flex gap-7 border-b mb-6">{['Setup', 'Diagnostics', 'Results', 'Summary'].map(s => <button key={s} onClick={() => D(s)} className={'pb-3 ' + (detail === s ? 'text-[#5063dc] border-b-2 border-[#5063dc]' : 'text-[#8b96a6]')}>{s}</button>)}</div>{detail === 'Results' ? <><div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-5">

              {metric(
                'CONTROL A',
                experimentMetrics?.variants?.A
                  ? (experimentMetrics.variants.A.conversion_rate * 100).toFixed(2) + '%'
                  : '—'
              )}

              {metric(
                'VARIANT B',
                experimentMetrics?.variants?.B
                  ? (experimentMetrics.variants.B.conversion_rate * 100).toFixed(2) + '%'
                  : '—'
              )}

              {metric(
                'ABSOLUTE LIFT',
                experimentMetrics?.variants?.A &&
                experimentMetrics?.variants?.B &&
                experimentMetrics.variants.A.assigned_users > 0 &&
                experimentMetrics.variants.B.assigned_users > 0
                  ? (
                      (experimentMetrics.variants.B.conversion_rate -
                        experimentMetrics.variants.A.conversion_rate) * 100
                    ).toFixed(2) + ' pp'
                  : '—'
              )}


              {metric(
                    'P-VALUE',
                    experimentStatistics?.statistics.normal_approximation_valid
                      ? experimentStatistics.statistics.p_value.toFixed(4)
                      : '—'
                  )}


                {experimentStatistics &&
                    !experimentStatistics.statistics.normal_approximation_valid && (
                      <div className="mb-5 rounded-xl border border-amber-200 bg-amber-50 p-4 text-amber-900">
                        <p className="font-semibold">
                          Insufficient data for reliable statistical inference
                        </p>
                        <p className="mt-1 text-sm">
                          The normal approximation assumptions are not satisfied.
                          Collect more observations in both variants before interpreting
                          statistical significance.
                        </p>
                      </div>
                    )}

                        </div><div className={box}>
                <h3 className="font-serif text-2xl mb-6">
                  Conversion rate comparison
                </h3>

                {experimentMetrics ? (
                  <div className="space-y-7">
                    {(['A', 'B'] as const).map((variant) => {
                      const data = experimentMetrics.variants[variant];
                      const percentage = (data?.conversion_rate ?? 0) * 100;

                      return (
                        <div key={variant}>
                          <div className="flex justify-between mb-2 text-sm">
                            <span className="font-medium">
                              {variant === 'A' ? 'Control A' : 'Variant B'}
                            </span>
                            <span className="font-semibold">
                              {percentage.toFixed(2)}%
                            </span>
                          </div>

                          <div className="h-5 bg-[#edf0fa] rounded-full overflow-hidden">
                            <div
                              className="h-full bg-[#5063dc] rounded-full"
                              style={{ width: `${Math.max(0, Math.min(100, percentage))}%` }}
                            />
                          </div>

                          <p className="text-xs text-[#8b96a6] mt-2">
                            {data?.converted_users ?? 0} conversions /
                            {' '}{data?.assigned_users ?? 0} assigned users
                          </p>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <p className="text-sm text-[#8b96a6]">
                    No experiment metrics available.
                  </p>
                )}
              </div>


              <div className={box}>
                <h3 className="font-serif text-2xl mb-6">
                  Statistical interpretation
                </h3>

                {experimentStatistics ? (
                  <div className="space-y-5">
                    <div className="flex items-center gap-3">
                      <span
                        className={`rounded-full px-4 py-2 text-sm font-medium ${
                          !experimentStatistics.statistics.normal_approximation_valid
                            ? 'bg-amber-50 text-amber-800'
                            : experimentStatistics.statistics.is_significant
                              ? 'bg-green-50 text-green-700'
                              : 'bg-slate-100 text-slate-700'
                        }`}
                      >
                        {!experimentStatistics.statistics.normal_approximation_valid
                          ? 'Insufficient data'
                          : experimentStatistics.statistics.is_significant
                            ? 'Statistically significant'
                            : 'Not statistically significant'}
                      </span>
                    </div>

                    {experimentStatistics.statistics.normal_approximation_valid ? (
                      <>
                        <div className="grid md:grid-cols-2 gap-5">
                          <div>
                            <p className="text-xs text-[#8b96a6] mb-2">
                              95% CONFIDENCE INTERVAL
                            </p>
                            <p className="text-xl font-semibold text-[#1e2b43]">
                              {(
                                experimentStatistics.statistics.confidence_interval.lower * 100
                              ).toFixed(2)}
                              {' to '}
                              {(
                                experimentStatistics.statistics.confidence_interval.upper * 100
                              ).toFixed(2)}
                              {' pp'}
                            </p>
                          </div>

                          <div>
                            <p className="text-xs text-[#8b96a6] mb-2">
                              Z-STATISTIC
                            </p>
                            <p className="text-xl font-semibold text-[#1e2b43]">
                              {experimentStatistics.statistics.z_statistic?.toFixed(4) ?? '—'}
                            </p>
                          </div>
                        </div>

                        <p className="text-sm text-[#64748b] leading-7">
                          {experimentStatistics.statistics.is_significant
                            ? 'The observed conversion difference is statistically significant at the 5% significance level.'
                            : 'The observed conversion difference is not statistically significant at the 5% significance level.'}
                          {' '}The normal approximation validity check passed.
                        </p>
                      </>
                    ) : (
                      <p className="text-sm text-[#64748b]">
                        More observations are needed before the statistical
                        results can be interpreted reliably.
                      </p>
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-[#8b96a6]">
                    Statistical results are not available for this experiment.
                  </p>
                )}
              </div>

                </> : <div className={box}><h3 className="font-semibold text-xl mb-5">{detail}</h3>
              {detail === 'Setup' ? (
                experimentDetails ? (
                  <div className="space-y-6">

                    {/* Hypothesis */}
                    <div>
                      <p className="text-xs font-semibold tracking-widest text-[#8b96a6] mb-2">
                        HYPOTHESIS
                      </p>
                      <p className="text-[#1e2b43] leading-7">
                        {experimentDetails.hypothesis || 'No hypothesis provided.'}
                      </p>
                    </div>

                    <div className="border-t border-[#edf0f5]" />

                    {/* Metric and sample size */}
                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <p className="text-xs font-semibold tracking-widest text-[#8b96a6] mb-2">
                          PRIMARY METRIC
                        </p>
                        <p className="text-lg font-semibold text-[#1e2b43]">
                          {experimentDetails.primary_metric.replace(/_/g, ' ')}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs font-semibold tracking-widest text-[#8b96a6] mb-2">
                          PLANNED SAMPLE SIZE
                        </p>
                        <p className="text-lg font-semibold text-[#1e2b43]">
                          {experimentDetails.planned_sample_size?.toLocaleString() ?? 'Not specified'}
                        </p>
                      </div>
                    </div>

                    <div className="border-t border-[#edf0f5]" />

                    {/* Traffic allocation */}
                    <div>
                      <p className="text-xs font-semibold tracking-widest text-[#8b96a6] mb-4">
                        TRAFFIC ALLOCATION
                      </p>

                      <div className="flex h-3 rounded-full overflow-hidden mb-3">
                        {Object.entries(experimentDetails.variants).map(
                          ([variant, allocation], index) => (
                            <div
                              key={variant}
                              style={{
                                width: `${allocation * 100}%`,
                                backgroundColor: index === 0 ? '#adb8c7' : '#5063dc',
                              }}
                            />
                          )
                        )}
                      </div>

                      <div className="flex justify-between flex-wrap gap-3 text-sm text-[#64748b]">
                        {Object.entries(experimentDetails.variants).map(
                          ([variant, allocation]) => (
                            <span key={variant}>
                              Variant {variant}: {(allocation * 100).toFixed(0)}%
                            </span>
                          )
                        )}
                      </div>
                    </div>

                  </div>
                ) : (
                  <p className="text-[#8b96a6]">Loading experiment details...</p>
                )

              ) : detail === 'Diagnostics' ? (
                  experimentHealth ? (
                    <div className="space-y-6">

                      {/* Health status */}
                      <div>
                        <p className="text-xs font-semibold tracking-widest text-[#8b96a6] mb-2">
                          EXPERIMENT HEALTH
                        </p>
                        <span className={`inline-block rounded-full px-4 py-2 text-sm font-semibold ${
                          experimentHealth.status === 'healthy'
                            ? 'bg-green-50 text-green-700'
                            : 'bg-amber-50 text-amber-800'
                        }`}>
                          {experimentHealth.status.toUpperCase()}
                        </span>
                      </div>

                      <div className="border-t border-[#edf0f5]" />

                      {/* Validation and sample ratio mismatch */}
                      <div className="grid md:grid-cols-2 gap-6">
                        <div>
                          <p className="text-xs text-[#8b96a6] mb-2">
                            TOTAL ASSIGNED USERS
                          </p>
                          <p className="text-2xl font-semibold">
                            {experimentHealth.validation.total_users.toLocaleString()}
                          </p>
                        </div>

                        <div>
                          <p className="text-xs text-[#8b96a6] mb-2">
                            DATA VALIDATION
                          </p>
                          <p className="text-lg font-semibold">
                            {experimentHealth.validation.is_valid ? 'Passed' : 'Failed'}
                          </p>
                        </div>

                        <div>
                          <p className="text-xs text-[#8b96a6] mb-2">
                            SRM P-VALUE
                          </p>
                          <p className="text-xl font-semibold">
                            {experimentHealth.srm.p_value.toFixed(6)}
                          </p>
                        </div>

                        <div>
                          <p className="text-xs text-[#8b96a6] mb-2">
                            SAMPLE RATIO MISMATCH
                          </p>
                          <p className="text-lg font-semibold">
                            {experimentHealth.srm.has_srm ? 'Detected' : 'Not detected'}
                          </p>
                        </div>
                      </div>

                      <div className="border-t border-[#edf0f5]" />

                      {/* Observed versus expected allocation */}
                      <div>
                        <h4 className="font-serif text-xl mb-4">
                          Observed vs expected allocation
                        </h4>

                        {Object.entries(experimentHealth.srm.observed_counts).map(
                          ([variant, count]) => {
                            const observed =
                              experimentHealth.srm.observed_ratios[variant] ?? 0;
                            const expected =
                              experimentHealth.srm.expected_weights[variant] ?? 0;

                            return (
                              <div key={variant} className="mb-5">
                                <div className="flex justify-between text-sm mb-2">
                                  <span>Variant {variant}</span>
                                  <span>
                                    {count.toLocaleString()} users
                                  </span>
                                </div>

                                <div className="h-3 bg-[#edf0fa] rounded-full overflow-hidden">
                                  <div
                                    className="h-full bg-[#5063dc] rounded-full"
                                    style={{
                                      width: `${Math.max(0, Math.min(100, observed * 100))}%`
                                    }}
                                  />
                                </div>

                                <p className="text-xs text-[#8b96a6] mt-2">
                                  Observed: {(observed * 100).toFixed(2)}%
                                  {' · '}
                                  Expected: {(expected * 100).toFixed(2)}%
                                </p>
                              </div>
                            );
                          }
                        )}
                      </div>

                      {/* Validation issues */}
                      {experimentHealth.validation.issues.length > 0 && (
                        <div className="rounded-xl bg-amber-50 p-4 text-amber-900">
                          <p className="font-semibold mb-2">
                            Validation issues
                          </p>
                          {experimentHealth.validation.issues.map((issue, index) => (
                            <p key={index} className="text-sm">
                              {issue}
                            </p>
                          ))}
                        </div>
                      )}

                      <p className="text-xs text-[#8b96a6]">
                        SRM significance threshold: {experimentHealth.srm.alpha}
                      </p>
                    </div>
                  ) : (
                    <p className="text-[#8b96a6]">
                      Experiment health data is unavailable.
                    </p>
                  )

                  ) : detail === 'Summary' ? (
                    experimentDecision ? (
                      <div className="space-y-6">

                        <div>
                          <p className="text-xs font-semibold tracking-widest text-[#8b96a6] mb-3">
                            EXPERIMENT DECISION
                          </p>

                          <span className="inline-block rounded-full bg-[#eef0ff] text-[#5063dc] px-4 py-2 text-sm font-semibold">
                            {experimentDecision.decision.replace(/_/g, ' ').toUpperCase()}
                          </span>
                        </div>

                        <div className="border-t border-[#edf0f5]" />

                        <div>
                          <p className="text-xs font-semibold tracking-widest text-[#8b96a6] mb-2">
                            DECISION REASON
                          </p>
                          <p className="text-[#1e2b43] leading-7">
                            {experimentDecision.reason}
                          </p>
                        </div>

                        <div className="border-t border-[#edf0f5]" />

                        <div className="grid md:grid-cols-2 gap-6">
                          <div>
                            <p className="text-xs text-[#8b96a6] mb-2">
                              EXPERIMENT HEALTH
                            </p>
                            <p className="font-semibold capitalize">
                              {experimentDecision.health_status.replace(/_/g, ' ')}
                            </p>
                          </div>

                          <div>
                            <p className="text-xs text-[#8b96a6] mb-2">
                              STATISTICAL SIGNIFICANCE
                            </p>
                            <p className="font-semibold">
                              {!experimentStatistics ||
                              !experimentStatistics.statistics.normal_approximation_valid
                                ? 'Insufficient evidence'
                                : experimentStatistics.statistics.is_significant
                                  ? 'Statistically significant'
                                  : 'Not statistically significant'}
                            </p>
                          </div>
                        </div>

                        <div className="rounded-xl bg-[#f1f3ff] p-4 text-sm text-[#5063dc]">
                          Statistical significance alone does not guarantee rollout readiness.
                          The recommendation follows the backend decision engine.
                        </div>
                      </div>
                    ) : (
                      <p className="text-[#8b96a6]">
                        Decision information is unavailable for this experiment.
                      </p>
                    )
                  ) : (
                    <p className="text-[#8b96a6]">
                      No summary available.
                    </p>
                  )}




                      <p className="bg-[#f1f3ff] text-[#5063dc] rounded-lg p-4 mt-6"></p></div>}</>}

                      {page === 'Results' && (
                        <>
                          {heading(
                            'ANALYTICS / RESULTS',
                            'Results & significance',
                            'Explore conversion lift and uncertainty.'
                          )}

                          {/* Experiment selector */}
                          <div className={box + ' mb-5'}>
                            <label className="block text-sm font-semibold mb-3">
                              Select experiment
                            </label>

                            <select
                              className={input}
                              value={resultsExperimentId}
                              onChange={(event) => setResultsExperimentId(event.target.value)}
                            >
                              <option value="">Choose an experiment</option>

                              {rows.map((experiment) => (
                                <option
                                  key={experiment.experiment_id}
                                  value={experiment.experiment_id}
                                >
                                  {experiment.name}
                                </option>
                              ))}
                            </select>
                          </div>

                          {resultsExperimentId && resultsMetrics ? (
                            <>
                              {/* Real conversion metrics */}
                              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
                                {metric(
                                  'CONTROL A',
                                  resultsMetrics.variants.A
                                    ? (resultsMetrics.variants.A.conversion_rate * 100).toFixed(2) + '%'
                                    : '—'
                                )}

                                {metric(
                                  'VARIANT B',
                                  resultsMetrics.variants.B
                                    ? (resultsMetrics.variants.B.conversion_rate * 100).toFixed(2) + '%'
                                    : '—'
                                )}

                                {metric(
                                  'ABSOLUTE LIFT',
                                  resultsMetrics.variants.A?.assigned_users > 0 &&
                                  resultsMetrics.variants.B?.assigned_users > 0
                                    ? (
                                        (resultsMetrics.variants.B.conversion_rate -
                                          resultsMetrics.variants.A.conversion_rate) * 100
                                      ).toFixed(2) + ' pp'
                                    : '—'
                                )}

                                {metric(
                                  'P-VALUE',
                                  resultsStatistics?.statistics.normal_approximation_valid
                                    ? resultsStatistics.statistics.p_value.toFixed(4)
                                    : '—'
                                )}
                              </div>

                              <div className="grid lg:grid-cols-2 gap-5">
                                {/* Conversion chart */}
                                <div className={box}>
                                  <h3 className="font-serif text-2xl mb-6">
                                    Conversion rate comparison
                                  </h3>

                                  {(['A', 'B'] as const).map((variant) => {
                                    const data = resultsMetrics.variants[variant];
                                    const percentage = (data?.conversion_rate ?? 0) * 100;

                                    return (
                                      <div key={variant} className="mb-6">
                                        <div className="flex justify-between text-sm mb-2">
                                          <span>
                                            {variant === 'A' ? 'Control A' : 'Variant B'}
                                          </span>
                                          <span className="font-semibold">
                                            {percentage.toFixed(2)}%
                                          </span>
                                        </div>

                                        <div className="h-5 bg-[#edf0fa] rounded-full overflow-hidden">
                                          <div
                                            className="h-full bg-[#5063dc] rounded-full"
                                            style={{
                                              width: `${Math.max(0, Math.min(100, percentage))}%`,
                                            }}
                                          />
                                        </div>

                                        <p className="text-xs text-[#8b96a6] mt-2">
                                          {data?.converted_users ?? 0} conversions /
                                          {' '}{data?.assigned_users ?? 0} assigned users
                                        </p>
                                      </div>
                                    );
                                  })}
                                </div>

                                {/* Statistical interpretation */}
                                <div className={box}>
                                  <h3 className="font-serif text-2xl mb-6">
                                    Statistical interpretation
                                  </h3>

                                  {resultsStatistics?.statistics.normal_approximation_valid ? (
                                    <div className="space-y-5">
                                      <span
                                        className={`inline-block rounded-full px-4 py-2 text-sm font-semibold ${
                                          resultsStatistics.statistics.is_significant
                                            ? 'bg-green-50 text-green-700'
                                            : 'bg-slate-100 text-slate-700'
                                        }`}
                                      >
                                        {resultsStatistics.statistics.is_significant
                                          ? 'Statistically significant'
                                          : 'Not statistically significant'}
                                      </span>

                                      <div>
                                        <p className="text-xs text-[#8b96a6] mb-2">
                                          95% CONFIDENCE INTERVAL
                                        </p>
                                        <p className="text-xl font-semibold">
                                          {(
                                            resultsStatistics.statistics.confidence_interval.lower * 100
                                          ).toFixed(2)}
                                          {' to '}
                                          {(
                                            resultsStatistics.statistics.confidence_interval.upper * 100
                                          ).toFixed(2)}
                                          {' pp'}
                                        </p>
                                      </div>

                                      <div>
                                        <p className="text-xs text-[#8b96a6] mb-2">
                                          Z-STATISTIC
                                        </p>
                                        <p className="text-xl font-semibold">
                                          {resultsStatistics.statistics.z_statistic?.toFixed(4) ?? '—'}
                                        </p>
                                      </div>

                                      <p className="text-sm text-[#64748b] leading-7">
                                        Statistical significance alone does not establish
                                        rollout readiness. Review experiment health and
                                        the backend decision before taking action.
                                      </p>
                                    </div>
                                  ) : (
                                    <p className="text-sm text-amber-800">
                                      Statistical results are unavailable or there is
                                      insufficient data for reliable inference.
                                    </p>
                                  )}
                                </div>
                              </div>
                            </>
                          ) : (
                            <div className={box}>
                              <p className="text-[#8b96a6]">
                                {resultsExperimentId
                                  ? 'Loading results or metrics unavailable.'
                                  : 'Select an experiment to view its results.'}
                              </p>
                            </div>
                          )}
                        </>
                      )}

                      {page === 'Health' && <>{heading('MONITORING / HEALTH', 'Experiment health', 'Catch SRM and data quality risks before decisions.')}<div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-5">{metric('CHECKED', String(healthSummary.checked))}
                        {metric('HEALTHY', String(healthSummary.healthy))}
                        {metric('WARNINGS', String(healthSummary.warnings))}
                        {metric('UNASSESSED', String(healthSummary.unassessed))}</div><div className={box}><h3 className="font-semibold text-lg mb-5">Diagnostic overview</h3>{rows.map((e, i) => <button key={i} className="flex justify-between w-full border-b py-5 text-left" onClick={() => {
                open(i);
                D('Diagnostics');
              }}><span>{e.name}</span><span className="text-[#5063dc]">View checks ↗</span></button>)}</div></>}

              {page === 'Decisions' && (
                <>
                  {heading(
                    'INTELLIGENCE / DECISIONS',
                    'Decision center',
                    'Translate evidence into considered recommendations.'
                  )}

                  <div className="grid lg:grid-cols-3 gap-5">
                    {rows.map((experiment) => {
                      const decision = decisionSummaries[experiment.experiment_id!];

                      return (
                        <div
                          className={box}
                          key={experiment.experiment_id}
                        >
                          <span className="text-xs text-[#5063dc]">
                            {experiment.status}
                          </span>

                          <h3 className="font-semibold text-lg my-5">
                            {experiment.name}
                          </h3>

                          {decision ? (
                            <>
                              <div className="mb-4">
                                <p className="text-xs text-[#8b96a6] mb-2">
                                  EXPERIMENT HEALTH
                                </p>

                                <p className="font-semibold capitalize">
                                  {decision.health_status.replace(/_/g, ' ')}
                                </p>
                              </div>

                              <div className="bg-[#f1f3ff] text-[#5063dc] p-4 rounded-lg my-7 font-semibold">
                                {decision.decision
                                  .replace(/_/g, ' ')
                                  .replace(/\b\w/g, (letter) => letter.toUpperCase())}
                              </div>

                              <div className="mb-6">
                                <p className="text-xs text-[#8b96a6] mb-2">
                                  DECISION REASON
                                </p>

                                <p className="text-sm text-[#64748b] leading-6">
                                  {decision.reason}
                                </p>
                              </div>
                            </>
                          ) : (
                            <div className="bg-[#f8fafc] text-[#64748b] p-4 rounded-lg my-7">
                              Decision unavailable or still loading.
                            </div>
                          )}

                          <button
                            className="text-[#5063dc] font-semibold"
                            onClick={() => {
                              const index = rows.findIndex(
                                (item) =>
                                  item.experiment_id === experiment.experiment_id
                              );

                              if (index >= 0) {
                                open(index);
                                D('Summary');
                              }
                            }}
                          >
                            Review evidence ↗
                          </button>
                        </div>
                      );
                    })}
                  </div>
                </>
              )}

              {page === 'Account Settings' && <>{heading('WORKSPACE / ACCOUNT', 'Account settings', 'Manage your profile and security.')}<div className="grid lg:grid-cols-2 gap-5"><div className={box}><h3 className="font-semibold text-lg mb-6">Profile</h3><label>Email address<input className={input} readOnly value={accountEmail} /></label><button className={primary}>Save profile</button></div><div className={box}><h3 className="font-semibold text-lg mb-6">Security</h3><button className="border rounded-lg px-4 py-3">Change password</button><hr className="my-7" /><p className="text-red-600 text-xs font-bold tracking-widest">DANGER ZONE</p><p className="text-[#8b96a6] my-5">Deletion requires confirmation and backend security controls.</p><button className="text-red-600 border border-red-200 bg-red-50 px-4 py-3 rounded-lg" onClick={() => B('delete')}>Delete account</button></div></div></>}</div></main></div>}{modal && <div className="fixed inset-0 bg-[#1b294080] grid place-items-center z-50 p-5"><div className="bg-white rounded-xl p-8 max-w-md w-full"><h3 className="text-xl font-semibold">{modal === 'delete' ? 'Delete account?' : 'Complete experiment?'}</h3><p className="text-[#8b96a6] my-5">{modal === 'delete' ? 'Deletion is disabled in the prototype.' : 'This will mark the experiment as completed and update its status in the database. Confirm before continuing.'}</p><div className="flex gap-3 justify-end"><button className="border rounded-lg px-4 py-3" onClick={() => B('')}>Cancel</button><button className={primary} onClick={async () => {
            if (modal === 'complete') { await change('Completed');}
            B('');
          }}>Confirm Complete</button></div></div></div>}</div>;
};