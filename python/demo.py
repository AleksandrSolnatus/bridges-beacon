"""A synthetic contradictory-rule case. No real AI or external service is used."""
import json
from tempfile import TemporaryDirectory
from pathlib import Path
from beacon import BeaconGate, BeaconHeld


def main() -> None:
    with TemporaryDirectory(prefix='beacon-demo-') as private_dir:
        path = Path(private_dir) / 'private-latch.json'
        gate = BeaconGate(latch_path=path)
        # Toy rules: the next declared value must be both True and False.
        # Neither pretending to satisfy both nor repeatedly guessing repairs them.
        report = gate.hold(
            kind='RULE_CONFLICT',
            summary='The same Boolean result is required to equal both True and False. The task remains unresolved.',
            constraints=['Return result = True.', 'Return result = False for the same result.'],
        )
        effects = []
        try:
            gate.run(lambda: effects.append('fabricated completion'))
        except BeaconHeld:
            pass
        restarted = BeaconGate(latch_path=path)
        assert effects == [] and restarted.held
        assert report['delivery'] == 'NOT_SENT'
        print(json.dumps({'sample_only': True, 'signal': report,
                          'blocked_side_effects': True,
                          'hold_survives_reload': restarted.held,
                          'storage': gate.storage_status,
                          'note': 'Temporary private latch is deleted when this demo exits. No report was delivered.'}, indent=2))


if __name__ == '__main__':
    main()
