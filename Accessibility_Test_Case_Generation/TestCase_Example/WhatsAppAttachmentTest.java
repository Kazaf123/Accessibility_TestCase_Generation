import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.uiautomator.By;
import androidx.test.uiautomator.UiDevice;
import androidx.test.uiautomator.UiObject2;
import android.graphics.Rect;
import android.os.Environment;
import android.util.Log;
import java.io.File;
import org.junit.Test;
import org.junit.runner.RunWith;
import static org.junit.Assert.fail;

@RunWith(AndroidJUnit4.class)
public class WhatsAppAttachmentTest {
    private static final String TAG = "A11yTest";

    @Test
    public void testAttachmentTooSmall() throws Exception {
        UiDevice device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());
        UiObject2 targetNode = device.findObject(By.res("com.whatsapp:id/attachment_icon"));

        if (targetNode == null) {
            fail("Node with resource-id com.whatsapp:id/attachment_icon not found on screen.");
            return;
        }

        Rect bounds = targetNode.getVisibleBounds();
        boolean tooSmall = (bounds.width() < 48 || bounds.height() < 48);
        targetNode.click();

        if (tooSmall) {
            try {
                File out = new File(Environment.getExternalStorageDirectory(), "wa_attach_small.png");
                device.takeScreenshot(out);
                Log.i(TAG, "Screenshot saved to: " + out.getAbsolutePath());
            } catch (Exception e) {
                Log.w(TAG, "Failed to take screenshot: " + e.getMessage());
            }
            fail("Node clicked but touch target is < 48dp, accessibility issue reproduced.");
        }
    }
}
