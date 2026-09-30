# PowerShell script to synthesize narration audio for all 6 scenes using Windows SAPI SpeechSynthesizer
# Calibrated for full 3-minute executive video walkthrough (~175-180 seconds total)

$narrations = @(
    @{
        Id = 1
        File = "frontend/static/images/scene1.wav"
        Text = "Welcome to the official demonstration of JANA-GATISHAKTI, an open-source Sovereign Digital Public Infrastructure certified against all 9 DPGA indicators. In traditional public administration, citizen grievances remain trapped in siloed portals while capital budgets are allocated in top-down black boxes. JANA-GATISHAKTI unites vernacular citizen voice, GIS spatial intelligence, and mathematical optimization into one unified platform for equitable nation-building."
    },
    @{
        Id = 2
        File = "frontend/static/images/scene2.wav"
        Text = "In the GIS Command Cockpit, the dashboard integrates a high-performance, zero-API-key Esri Dark map engine with Uber H3 hexagonal spatial indexing. Notice the live infrastructure deficit overlays across Maharashtra and aspirational districts. When an administrator clicks on the Kasansur cluster in Gadchiroli, the inspector instantly surfaces its canonical Local Government Directory code, deficit severity of 78 percent, and historical grievance records."
    },
    @{
        Id = 3
        File = "frontend/static/images/scene3.wav"
        Text = "Next, we move to the Citizen Edge interface. Citizens can file grievances via WhatsApp chatbots, voice notes, or web forms in their native languages. Under the Digital Personal Data Protection Act 2023, our system enforces privacy by design. The two-pass Verhoeff algorithm scrubs twelve-digit Aadhaar identifiers and phone numbers in-memory with zero data leakage, while Bhasha-Setu processes vernacular audio with transparent bilingual consent."
    },
    @{
        Id = 4
        File = "frontend/static/images/scene4.wav"
        Text = "In Tab 3, Nivesh-Drishti translates ground-level distress into institutional capital works. Here, the Kasansur drinking water crisis is automatically formulated into a bankable 14.5 Crore Rupee Jal Jeevan Mission project report, complete with population beneficiaries, technical milestones, and bill of quantities. Every proposal is structured compliant with the Open Contracting Data Standard 1.1 JSON format for public procurement."
    },
    @{
        Id = 5
        File = "frontend/static/images/scene5.wav"
        Text = "Tab 4 showcases the Policy and Capex Optimizer. Rather than relying on non-deterministic generative AI hallucinations, capital allocation is governed by Mixed-Integer Linear Programming using the PuLP and COIN-OR CBC solver. Policy makers can enforce statutory equity floors, guaranteeing that at least 40 percent of capital reaches Aspirational Districts and 30 percent reaches marginalized communities, solved in under 35 milliseconds."
    },
    @{
        Id = 6
        File = "frontend/static/images/scene6.wav"
        Text = "Finally, Tab 5 features the Jan-Praman Ghost Asset Sentinel. Post-construction verification is automated via AI-driven interactive voice calls to actual village residents. If a contractor reports a completed water pipe but citizens confirm dry taps, a red discrepancy flag automatically blocks payment clearance. Every inspection and decision is permanently committed to an immutable SHA-256 hash-chained audit ledger with verifiable Merkle roots. Thank you for exploring JANA-GATISHAKTI."
    }
)

Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Rate = 0  # Standard clear professional presentation speed (~3 minutes total)

foreach ($n in $narrations) {
    Write-Host "Synthesizing Scene $($n.Id)..."
    $synth.SetOutputToWaveFile($n.File)
    $synth.Speak($n.Text)
}

$synth.Dispose()
Write-Host "All 6 scene voiceovers generated successfully!"
