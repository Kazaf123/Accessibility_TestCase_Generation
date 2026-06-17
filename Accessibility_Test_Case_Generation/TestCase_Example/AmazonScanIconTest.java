import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.uiautomator.By;
import androidx.test.uiautomator.UiDevice;
import androidx.test.uiautomator.UiObject2;
import android.os.Environment;
import android.util.Log;
import java.io.File;
import org.junit.Test;
import org.junit.runner.RunWith;
import static org.junit.Assert.fail;

@RunWith(AndroidJUnit4.class)
public class AmazonScanIconTest {
    private static final String TAG = "A11yTest";

    @Test
    public void testScanIconMissingLabel() throws Exception {
        UiDevice device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());
        UiObject2 targetNode = device.findObject(By.res("com.amazon.mShop.android.shopping:id/scan_barcode_btn"));

        if (targetNode == null) {
            fail("Node with resource-id com.amazon.mShop.android.shopping:id/scan_barcode_btn not found on screen.");
            return;
        }

        if (!targetNode.isFocusable()) {
            fail("Node is not focusable, cannot simulate TalkBack interaction.");
            return;
        }

        CharSequence desc = targetNode.getContentDescription();
        boolean missingLabel = (desc == null || desc.toString().trim().isEmpty());
        targetNode.click();

        if (missingLabel) {
            try {
                File out = new File(Environment.getExternalStorageDirectory(), "amz_scan_nolabel.png");
                device.takeScreenshot(out);
                Log.i(TAG, "Screenshot saved to: " + out.getAbsolutePath());
            } catch (Exception e) {
                Log.w(TAG, "Failed to take screenshot: " + e.getMessage());
            }
            fail("Node clicked but missing contentDescription (empty), accessibility issue reproduced.");
        }
    }
}
