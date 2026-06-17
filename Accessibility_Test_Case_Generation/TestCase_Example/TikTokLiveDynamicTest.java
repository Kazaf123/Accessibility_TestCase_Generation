import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.uiautomator.By;
import androidx.test.uiautomator.UiDevice;
import androidx.test.uiautomator.UiObject2;
import androidx.test.uiautomator.Until;
import android.os.Environment;
import android.util.Log;
import java.io.File;
import org.junit.Test;
import org.junit.runner.RunWith;
import static org.junit.Assert.fail;

@RunWith(AndroidJUnit4.class)
public class TikTokLiveDynamicTest {
    private static final String TAG = "A11yTest";

    @Test
    public void testLiveDynamic() throws Exception {
        UiDevice device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());
        UiObject2 triggerNode = device.findObject(By.res("com.zhiliaoapp.musically:id/live_entrance"));

        if (triggerNode == null) {
            fail("Trigger node not found on screen.");
            return;
        }

        triggerNode.click();

        boolean appeared = device.wait(Until.hasObject(By.res("com.zhiliaoapp.musically:id/live_comment_list")), 3000);
        if (appeared) {
            UiObject2 dynObj = device.findObject(By.res("com.zhiliaoapp.musically:id/live_comment_list"));
            boolean inaccessible = (!dynObj.isFocusable() && dynObj.getContentDescription() == null);
            if (inaccessible) {
                try {
                    File out = new File(Environment.getExternalStorageDirectory(), "tiktok_dyn.png");
                    device.takeScreenshot(out);
                    Log.i(TAG, "Screenshot saved to: " + out.getAbsolutePath());
                } catch (Exception e) {
                    Log.w(TAG, "Failed to take screenshot: " + e.getMessage());
                }
                fail("Dynamic element loaded but is inaccessible to TalkBack.");
            }
        }
    }
}
