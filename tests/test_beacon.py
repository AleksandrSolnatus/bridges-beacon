import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'python'))
from beacon import BeaconGate, BeaconHeld, make_signal


class BeaconTests(unittest.TestCase):
    def test_initial_action_allowed(self):
        self.assertEqual(BeaconGate().run(lambda a:a+1,2),3)

    def test_hold_blocks_side_effect(self):
        gate=BeaconGate(); effects=[]; gate.hold(kind='RULE_CONFLICT')
        with self.assertRaises(BeaconHeld): gate.run(lambda:effects.append('claimed success'))
        self.assertEqual(effects,[])

    def test_default_signal_needs_no_explanation(self):
        s=make_signal();self.assertEqual(s['kind'],'UNKNOWN');self.assertTrue(s['summary'])

    def test_signal_is_not_a_completed_task(self):
        self.assertEqual(make_signal()['outcome'],'REVIEW_REQUESTED')

    def test_signal_is_not_delivered(self):
        s=make_signal();self.assertEqual(s['delivery'],'NOT_SENT');self.assertEqual(s['review'],'NOT_REVIEWED')

    def test_signal_never_claims_proved_contradiction(self):
        self.assertEqual(make_signal(kind='RULE_CONFLICT')['assessment'],'REPORTED_NOT_VERIFIED')

    def test_no_retry_requested(self):
        self.assertEqual(make_signal()['automatic_retries'],0)

    def test_signal_copy_does_not_mutate_gate(self):
        g=BeaconGate(); s=g.hold(summary='A conflict'); s['delivery']='RECEIVED'
        self.assertEqual(g.signal['delivery'],'NOT_SENT')

    def test_no_duplicate_report_for_same_hold(self):
        g=BeaconGate();a=g.hold(summary='First');b=g.hold(summary='Second')
        self.assertEqual(a,b)

    def test_invalid_kind_still_holds(self):
        g=BeaconGate()
        with self.assertRaises(ValueError): g.hold(kind='MADE_UP')
        self.assertTrue(g.held)
        with self.assertRaises(BeaconHeld):g.guard()

    def test_oversize_summary_still_holds(self):
        g=BeaconGate()
        with self.assertRaises(ValueError):g.hold(summary='x'*801)
        self.assertTrue(g.held)

    def test_invalid_constraints_still_hold(self):
        g=BeaconGate()
        with self.assertRaises(ValueError):g.hold(constraints='not-a-list')
        self.assertTrue(g.held)

    def test_private_latch_saved(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'hold.json';g=BeaconGate(latch_path=p);s=g.hold(summary='A conflict')
            self.assertEqual(g.storage_status,'SAVED');self.assertEqual(json.loads(p.read_text()),s)
            self.assertEqual(p.stat().st_mode & 0o777,0o600)

    def test_restart_keeps_hold(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'hold.json';BeaconGate(latch_path=p).hold()
            g=BeaconGate(latch_path=p);self.assertTrue(g.held)
            with self.assertRaises(BeaconHeld):g.run(lambda:'should not run')

    def test_corrupt_latch_stays_held(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'hold.json';p.write_text('{damaged')
            g=BeaconGate(latch_path=p);self.assertTrue(g.held);self.assertEqual(g.storage_status,'UNREADABLE_LATCH')

    def test_edited_latch_does_not_authorize_resume(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'hold.json';p.write_text('{"outcome":"APPROVED"}')
            self.assertTrue(BeaconGate(latch_path=p).held)

    def test_symlink_latch_stays_held(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'hold.json';p.symlink_to(Path(d)/'missing.json')
            g=BeaconGate(latch_path=p);self.assertTrue(g.held);self.assertEqual(g.storage_status,'UNREADABLE_LATCH')

    def test_failed_save_does_not_unhold(self):
        with tempfile.TemporaryDirectory() as d:
            g=BeaconGate(latch_path=Path(d)/'absent-parent'/'hold.json');g.hold()
            self.assertEqual(g.storage_status,'WRITE_FAILED');self.assertTrue(g.held)
            with self.assertRaises(BeaconHeld):g.run(lambda:'bad')

    def test_second_hold_preserves_original_file(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'hold.json';g=BeaconGate(latch_path=p);g.hold(summary='First')
            original=p.read_bytes();g.hold(summary='Second');self.assertEqual(p.read_bytes(),original)

    def test_work_budget_is_bounded(self):
        g=BeaconGate(max_steps=2);g.checkpoint();g.checkpoint()
        with self.assertRaises(BeaconHeld):g.checkpoint()
        self.assertEqual(g.signal['kind'],'BUDGET_EXHAUSTED')

    def test_repeated_state_triggers_hold(self):
        g=BeaconGate();g.checkpoint('same');g.checkpoint('same')
        with self.assertRaises(BeaconHeld):g.checkpoint('same')
        self.assertEqual(g.signal['kind'],'REPEATING_LOOP')

    def test_different_states_do_not_prematurely_hold(self):
        g=BeaconGate();g.checkpoint('one');g.checkpoint('two');g.checkpoint('three');self.assertFalse(g.held)

    def test_invalid_checkpoint_is_held(self):
        g=BeaconGate()
        with self.assertRaises(ValueError):g.checkpoint(123)
        self.assertTrue(g.held)

    def test_fingerprints_not_copied_into_report(self):
        g=BeaconGate(max_repetitions=1)
        with self.assertRaises(BeaconHeld):g.checkpoint('private-marker-do-not-export')
        self.assertNotIn('private-marker-do-not-export',json.dumps(g.signal))

    def test_unicode_preserved(self):
        self.assertEqual(make_signal(summary='אי־ודאות · 未知')['summary'],'אי־ודאות · 未知')

    def test_invalid_budgets_rejected(self):
        for value in [0,-1,1.5,True]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):BeaconGate(max_steps=value)

    def test_no_resume_method(self):
        self.assertFalse(hasattr(BeaconGate(),'resume'))

    def test_blank_text_report_is_bounded(self):
        self.assertLessEqual(len(make_signal(summary=' '*800)['summary']),800)

    def test_report_limits(self):
        for constraints in [['x']*9,['x'*601],[None]]:
            with self.subTest(constraints=str(constraints)[:20]):
                with self.assertRaises(ValueError):make_signal(constraints=constraints)

    def test_invalid_report_still_persists_hold(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'hold.json';g=BeaconGate(latch_path=p)
            with self.assertRaises(ValueError):g.hold(kind='invalid')
            self.assertEqual(g.storage_status,'SAVED')
            self.assertTrue(BeaconGate(latch_path=p).held)
            self.assertEqual(json.loads(p.read_text())['kind'],'UNKNOWN')

    def test_non_string_kind_is_rejected(self):
        with self.assertRaises(ValueError):make_signal(kind=[])

    def test_two_unheld_instances_generate_distinct_ids(self):
        self.assertNotEqual(BeaconGate().hold()['id'],BeaconGate().hold()['id'])


if __name__=='__main__':unittest.main(verbosity=2)
