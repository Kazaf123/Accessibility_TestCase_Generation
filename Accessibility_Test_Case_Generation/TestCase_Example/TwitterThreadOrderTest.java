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
public class TwitterThreadOrderTest {
    private static final String TAG = "A11yTest";

    @Test
    public void testThreadFocusOrder() throws Exception {
        UiDevice device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());
        UiObject2 firstNode = device.findObject(By.res("com.twitter.android:id/action_bar"));
        UiObject2 secondNode = device.findObject(By.res("com.twitter.android:id/tweet_text"));

        if (firstNode == null || secondNode == null) {
            fail("Target nodes not found on screen.");
            return;
        }

        boolean abnormalOrder = (firstNode.getVisibleBounds().bottom > secondNode.getVisibleBounds().top);

        if (abnormalOrder) {
            try {
                File out = new File(Environment.getExternalStorageDirectory(), "tw_focus.png");
                device.takeScreenshot(out);
                Log.i(TAG, "Screenshot saved to: " + out.getAbsolutePath());
            } catch (Exception e) {
                Log.w(TAG, "Failed to take screenshot: " + e.getMessage());
            }
            fail("Focus reading order contradicts visual layout, accessibility issue reproduced.");
        }
    }
}
